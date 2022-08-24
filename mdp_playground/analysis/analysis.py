import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import warnings

class MDPP_Analysis():
    '''Utility class to load and plot data for analysis of experiments from MDP Playground

    '''
    def __init__(self):
        pass

    def load_data(self, dir_name, exp_name, num_metrics=3, load_eval=False): #, max_total_configs=200):
        '''Loads training and evaluation data from given file

        Parameters
        ----------
        dir_name : str
            The location where the training and evaluation CSV files were written
        exp_name : str
            The name of the experiment: the training and evaluation CSV filenames are formed using this string

        Returns
        -------
        train_stats : np.ndarray
            Training stats at end of training: 8-D tensor with 1st 6 dims the meta-features of MDP Playground, 7th dim is across the seeds, 8th dim is across different stats saved
        eval_stats : np.ndarray
            Training stats at end of training: 8-D tensor with 1st 6 dims the meta-features of MDP Playground, 7th dim is across the seeds, 8th dim is across different stats saved
        train_curves: np.ndarray
            The loaded training CSV with the last 3 columns the train stats that were saved and the initial columns are various setting for the algorithm and environment.
        eval_curves: np.ndarray
            The loaded evaluation CSV with the columns the evaluation stats that were saved
        '''

        stats_file = dir_name + '/' + exp_name #Name of file to which benchmark stats were written
        self.stats_file = stats_file

        if os.path.isfile(stats_file + '.csv'):
            print("Loading data from a sequential run/already combined runs of experiment configurations.")
        else:
            print("Loading data from a distributed run of experiment configurations. Creating a combined CSV stats file.")
            def join_files(file_prefix, file_suffix):
                '''Utility to join files that were written with different experiment configs'''
                with open(file_prefix + file_suffix, 'ab') as combined_file:
                    i = 0
                    missing_configs = []
                    num_diff_lines = []
                    while True: # i < max_total_configs:
                        if os.path.isfile(file_prefix + '_' + str(i) + file_suffix):
                            with open(file_prefix + '_' + str(i) + file_suffix, 'rb') as curr_file:
                                byte_string = curr_file.read()
                                newline_count = byte_string.count(10)
                                num_diff_lines.append(newline_count)
                                # if newline_count != 21 and file_suffix == '.csv': #hack to check only train files and not eval
                                #     warnings.warn('Expected 21 \\n chars in each stats file because we usually write stats every 1k timesteps for 20k timesteps. However, this can easily differ, e.g., for TD3 and DDPG where learning starts at 2k timesteps and there is 1 less \\n. Got only: ' + str(newline_count) + ' in file: ' + str(i))
                                combined_file.write(byte_string)
                        else:
                            # missing_configs.append(i)
                            break
                        i += 1
                    print(str(i) + " files were combined into 1 for file:" + file_prefix + '_n' + file_suffix)
                    # print("Files missing for config_nums:", missing_configs, ". Did you pass the right value for max_total_configs as an argument?")
                    # print("Unique line count values:", np.unique(num_diff_lines))
                    if i==0:
                        raise FileNotFoundError("No files to combine were present. Please check your location and/or filenames that they are correct.")
            join_files(stats_file,  '.csv')
            if load_eval:
                join_files(stats_file, '_eval.csv')

        stats_pd = pd.read_csv(stats_file + '.csv', skip_blank_lines=True, header=None, comment='#', sep=' ')
        # print(stats_pd)
        # print(stats_pd[11].dtypes)
        # print(stats_pd.dtypes)
        print("Training stats read (rows, columns):", stats_pd.shape)

        # Read column names
        with open(stats_file + '.csv') as file_:
            config_names = file_.readline().strip().split(', ')
            config_names[0] = config_names[0][2:] # to remove '# ' that was written
            # config_names[-1] = config_names[-1][:-1] # to remove ',' that was written
        # print("config_names:", config_names)
        self.config_names = config_names[1:] # ; begins at 1 to ignore training iteration num. ['Delay', 'Sequence Length', 'Reward Density', 'Terminal State Density', 'P Noise', 'R Noise', 'dummy_seed']
        config_counts = []
        dims_values = []
        # For the following seeds should always be last column read! 1st column should be >=1 (it should not be 0 because that is the training_iteration that was recorded and is not used here)
        for i in range(1, len(config_names) - num_metrics): # hardcoded 3 for no. of stats written
            dims_values.append(stats_pd[i].unique())
            config_counts.append(stats_pd[i].nunique())

        # config_counts[2] = 1 # hack
        # config_counts[-1] = 2 # hack for TD3 HP tuning files
        config_counts.append(num_metrics) #hardcoded number of training stats that were recorded
        config_counts = tuple(config_counts)
        self.metric_names = config_names[-num_metrics:]

        # Slice into training stats and get end of training stats for individual training runs in the experiment
        final_rows_for_a_config = []
        previous_i = 0
        list_of_learning_curves = []
        # cols_to_take = 8

        for i in range(stats_pd.shape[0] - 1):
            if stats_pd.iloc[i, -num_metrics] > stats_pd.iloc[i + 1, -num_metrics]: # hardcoded: -num_metrics column always HAS to be no. of timesteps for the current run
                # list_of_learning_curves.append(stats_pd.iloc[previous_i:i+1, -cols_to_take:])
                previous_i = i + 1
                final_rows_for_a_config.append(i)
        # print("i, previous_i:", i, previous_i)
        final_rows_for_a_config.append(i + 1) # Always append the last row!
        # list_of_learning_curves.append(stats_pd.iloc[previous_i:i + 2, -cols_to_take:])
        self.final_rows_for_a_config = final_rows_for_a_config

        # print(len(list_of_learning_curves))
        # print(len(final_rows_for_a_config))
        stats_end_of_training = stats_pd.iloc[final_rows_for_a_config]
        stats_reshaped = stats_end_of_training.iloc[:, -num_metrics:] # hardcoded # last vals are timesteps_total, episode_reward_mean, episode_len_mean
        stats_reshaped = np.reshape(np.array(stats_reshaped), config_counts)
        # print(stats_end_of_training.head(10))
        print("train stats shape:", stats_reshaped.shape)
#         to_plot_ = np.squeeze(stats_reshaped[:, :, :, :, 0, 0, :, 1])
#         print('Episode reward (at end of training) for 10 seeds for vanilla env.:', to_plot_)


        eval_stats = None
        mean_data_eval = None
        final_eval_metrics_reshaped = None
        if load_eval:
            # Load evaluation stats
            stats_file_eval = stats_file + '_eval.csv'
            eval_stats = np.loadtxt(stats_file_eval, dtype=float)
            # print(eval_stats, eval_stats.shape)

            i = 0
            hack_indices = []
            for line in open(stats_file_eval):

                line=line.strip()
            #    print(line)
                if line.startswith("#HACK"):
            #         print(line, i)
                    hack_indices.append(i - len(hack_indices)) # appends index of last eval in this training_iteration
                i += 1

            # print(len(hack_indices), hack_indices)
            if hack_indices[0] == 0: #hack
                hack_indices = hack_indices[1:] #hardcoded removes the 1st hack_index which is at position 0 so that hack_indices_10 below doesn't begin with a -10; apparently Ray seems to have changed logging for evaluation (using on_episode_end) from 0.7.3 to 0.9.0
                ray_0_9_0 = True
            else:
                ray_0_9_0 = False
            hack_indices_10 = np.array(hack_indices) - 10
            # print(hack_indices_10.shape, hack_indices_10)
            # print(np.array(hack_indices[1:]) - np.array(hack_indices[:-1]))
            # print("Min:", min(np.array(hack_indices[1:]) - np.array(hack_indices[:-1]))) # Some problem with Ray? Sometimes no. of eval episodes is less than 10.
            final_10_evals = []
            for i in range(len(hack_indices)):
                final_10_evals.append(eval_stats[hack_indices_10[i]:hack_indices[i]])
            #     print(final_10_evals[-1])
            if ray_0_9_0: #hack
                final_10_evals.append(eval_stats[hack_indices[i]:]) # appends the very last eval which begins at last hack_index for Ray 0.9.0

            final_10_evals = np.array(final_10_evals) # has 2 columns: episode reward and episode length
            # print(final_10_evals.shape, final_10_evals)


            # final_vals = fin[final_rows_for_a_config]
            # print('final_rows_for_a_config', final_rows_for_a_config)
            # print("len(final_10_evals)", final_10_evals.shape, type(final_10_evals))
            mean_data_eval = np.mean(final_10_evals, axis=1) # this is mean over last 10 eval episodes
    #         print(np.array(stats_pd.iloc[:, -3]))

            # Adds timesteps_total column to the eval stats which did not have them:
            mean_data_eval = np.concatenate((np.atleast_2d(np.array(stats_pd.iloc[:, -num_metrics])).T, mean_data_eval), axis=1)
    #         print(mean_data_eval.shape, len(final_rows_for_a_config))


            final_eval_metrics_ = mean_data_eval[final_rows_for_a_config, :] # 1st column is episode reward, 2nd is episode length in original _eval.csv file, here it's 2nd and 3rd after prepending timesteps_total column above.
            # print(dims_values, config_counts)
            final_eval_metrics_reshaped = np.reshape(final_eval_metrics_, config_counts)
            # print(final_eval_metrics_)
    #         print("eval stats shapes (before and after reshape):", final_eval_metrics_.shape, final_eval_metrics_reshaped.shape)
            print("eval stats shape:", final_eval_metrics_reshaped.shape)

        self.config_counts = config_counts[:-1] # -1 is added to ignore "no. of stats that were saved" as dimensions of difficulty
        self.dims_values = dims_values

        # Catpure the dimensions that were varied, i.e. ones which had more than 1 value across experiments
        x_axis_labels = []
        x_tick_labels_ = []
        dims_varied = []
        for i in range(len(self.config_counts) - 1): # -1 is added to ignore #seeds as dimensions of difficulty
            if self.config_counts[i]> 1:
                x_axis_labels.append(self.config_names[i])
                x_tick_labels_.append([str(j) for j in self.dims_values[i]])
                for j in range(len(x_tick_labels_[-1])):
                    if len(x_tick_labels_[-1][j]) > 2: #hack
                        abridged_str = x_tick_labels_[-1][j].split(',')
                        if abridged_str[-1] == '':
                            abridged_str = abridged_str[:-1]
                        for k in range(len(abridged_str)):
                            if abridged_str[k] == 'scale':
                                abridged_str[k] = 'S'
                            elif abridged_str[k] == 'shift':
                                abridged_str[k] = 's'
                            elif abridged_str[k] == 'rotate':
                                abridged_str[k] = 'r'
                            elif abridged_str[k] == 'flip':
                                abridged_str[k] = 'f'
                            # abridged_str[j] = abridged_str[j][:2]
                        x_tick_labels_[-1][j] = ''.join(abridged_str)
                dims_varied.append(i)

        self.axis_labels = x_axis_labels
        self.tick_labels = x_tick_labels_
        self.dims_varied = dims_varied
        for d,v,i in zip(x_axis_labels, x_tick_labels_, dims_varied):
            print("Dimension varied:", d, ". The values it took:", v, ". Number of values it took:", config_counts[i], ". Index in loaded data:", i)

        return stats_reshaped, final_eval_metrics_reshaped, np.array(stats_pd), mean_data_eval


    def plot_1d_dimensions(self, stats_data, save_fig=False, train=True, metric_num=-2):
        '''Plots 1-D bar plots across a single dimension with mean and std. dev.

        Parameters
        ----------
        stats_data : np.array
            8-D tensor with 1st 6 dims the meta-features of MDP Playground, 7th dim is across the seeds, 8th dim is across different stats saved
        save_fig : bool, optional
            A flag used to save a PDF (default is
            False)
        train : bool, optional
            A flag used to insert either _train or _eval in the filename of the PDF (default is True)

        '''
        y_axis_label = 'Reward' if 'reward' in self.metric_names[metric_num] else self.metric_names[metric_num]

        plt.rcParams.update({'font.size': 18}) # default 12, for poster: 30
        # print(stats_data.shape)

        mean_data_ = np.mean(stats_data[..., metric_num], axis=-1) # the slice sub-selects the metric written in position metric_num from the "last axis of diff. metrics that were written" and then the axis of #seeds becomes axis=-1 ( before slice it was -2).
        to_plot_ = np.squeeze(mean_data_)
        std_dev_ = np.std(stats_data[..., metric_num], axis=-1) #seed
        to_plot_std_ = np.squeeze(std_dev_)

        fig_width = len(self.tick_labels[0])
        # plt.figure()
        plt.figure(figsize=(fig_width, 1.5))

        # print(to_plot_.shape)
        if len(to_plot_.shape) == 2: # Case when 2 meta-features were varied
            plt.bar(self.tick_labels[0], to_plot_[:, 0], yerr=to_plot_std_[:, 0])
        else:
            plt.bar(self.tick_labels[0], to_plot_, yerr=to_plot_std_)
        plt.xlabel(self.axis_labels[0])
        plt.ylabel(y_axis_label)
        if save_fig:
            plt.savefig(self.stats_file.split('/')[-1] + ('_train' if train else '_eval') + '_final_reward_' + self.axis_labels[0].replace(' ','_') + '_' + str(self.metric_names[metric_num]) + '_1d.pdf', dpi=300, bbox_inches="tight")
        plt.show()

        if len(to_plot_.shape) == 2: # Case when 2 meta-features were varied
            fig_width = len(self.tick_labels[1])
            plt.figure(figsize=(fig_width, 1.5))
            plt.bar(self.tick_labels[1], to_plot_[0, :], yerr=to_plot_std_[0, :])
            # plt.tight_layout()
            plt.xlabel(self.axis_labels[1])
            plt.ylabel(y_axis_label)
            if save_fig:
                plt.savefig(self.stats_file.split('/')[-1] + ('_train' if train else '_eval') + '_final_reward_' + self.axis_labels[1].replace(' ','_') + '_' + str(self.metric_names[metric_num]) + '_1d.pdf', dpi=300, bbox_inches="tight")
            plt.show()

    def plot_2d_heatmap(self, stats_data, save_fig=False, train=True, metric_num=-2):
        '''Plots 2 2-D heatmaps: 1 for mean and 1 for std. dev. across 2 meta-features of MDP Playground

        Parameters
        ----------
        stats_data : np.array
            8-D tensor with 1st 6 dims the meta-features of MDP Playground, 7th dim is across the seeds, 8th dim is across different stats saved
        save_fig : bool, optional
            A flag used to save a PDF (default is
            False)
        train : bool, optional
            A flag used to insert either _train or _eval in the filename of the PDF (default is True)
        '''
        plt.rcParams.update({'font.size': 18}) # default 12, 24 for paper, for poster: 30
        cmap = 'Purples' # 'Blues' #
        label_ = 'Reward' if 'reward' in self.metric_names[metric_num] else self.metric_names[metric_num]

        mean_data_ = np.mean(stats_data[..., metric_num], axis=-1) #seed
        to_plot_ = np.squeeze(mean_data_)
        # print(to_plot_)
        if len(to_plot_.shape) > 2:
            # warning.warn("Data contains variation in more than 2 dimensions (apart from seeds). May lead to plotting error!")
            raise ValueError("Data contains variation in more than 2 dimensions (apart from seeds). This is currently not supported") #TODO Add 2-D plots for all combinations of 2 varying dims?
        plt.imshow(np.atleast_2d(to_plot_), cmap=cmap, interpolation='none', vmin=0, vmax=np.max(to_plot_))
        if len(self.tick_labels) == 2:
            plt.gca().set_xticklabels(self.tick_labels[1])
            plt.gca().set_yticklabels(self.tick_labels[0])
        else:
            plt.gca().set_xticklabels(self.tick_labels[0])
        cbar = plt.colorbar()
        cbar.ax.get_yaxis().labelpad = 15 # default 15, for poster: 25
        cbar.set_label(label_, rotation=270)
        if len(self.axis_labels) == 2:
            plt.xlabel(self.axis_labels[1])
            plt.ylabel(self.axis_labels[0])
        else:
            plt.xlabel(self.axis_labels[0])
        if save_fig:
            plt.savefig(self.stats_file.split('/')[-1] + ('_train' if train else '_eval') + '_final_reward_mean_heat_map_' + str(self.metric_names[metric_num]) + '.pdf', dpi=300, bbox_inches="tight")
        plt.show()
        std_dev_ = np.std(stats_data[..., metric_num], axis=-1) #seed
        to_plot_ = np.squeeze(std_dev_)
        # print(to_plot_, to_plot_.shape)
        plt.imshow(np.atleast_2d(to_plot_), cmap=cmap, interpolation='none', vmin=0, vmax=np.max(to_plot_)) # 60 for DQN, 100 for A3C
        if len(self.tick_labels) == 2:
            plt.gca().set_xticklabels(self.tick_labels[1])
            plt.gca().set_yticklabels([str(i) for i in self.tick_labels[0]])
        else:
            plt.gca().set_xticklabels(self.tick_labels[0])
        cbar = plt.colorbar()
        cbar.ax.get_yaxis().labelpad = 15 # default 15, for poster: 30
        cbar.set_label('Reward Std Dev.', rotation=270)
        if len(self.axis_labels) == 2:
            plt.xlabel(self.axis_labels[1])
            plt.ylabel(self.axis_labels[0])
        else:
            plt.xlabel(self.axis_labels[0])
        # plt.tight_layout()
        if save_fig:
            plt.savefig(self.stats_file.split('/')[-1] + ('_train' if train else '_eval') + '_final_reward_std_heat_map_' + str(self.metric_names[metric_num]) + '.pdf', dpi=300, bbox_inches="tight")
            # plt.savefig(stats_file.split('/')[-1] + '_train_heat_map.png')#, dpi=300)
        plt.show()

    def plot_learning_curves(self, stats_data, save_fig=False, train=True, metric_num=-2): # metric_num needs to be minus indexed because stats_pd reutrned for train stats has _all_ columns
        '''Plots learning curves: Either across 1 or 2 meta-features of MDP Playground. Different colours represent learning curves for different seeds.

        Parameters
        ----------
        stats_data : np.array
            8-D tensor with 1st 6 dims the meta-features of MDP Playground, 7th dim is across the seeds, 8th dim is across different stats saved
        save_fig : bool, optional
            A flag used to save a PDF (default is
            False)
        train : bool, optional
            A flag used to insert either _train or _eval in the filename of the PDF (default is True)
        '''
        # Plot for train metrics: learning curves; with subplot
        # Comment out unneeded labels in code lines 41-44 in this cell
        if len(self.dims_varied) > 1:
            ncols_ = self.config_counts[self.dims_varied[1]]
            nrows_ = self.config_counts[self.dims_varied[0]]
        else:
            ncols_ = self.config_counts[self.dims_varied[0]]
            nrows_ = 1
        nseeds_ = self.config_counts[-1]
        # print(ax, type(ax), type(ax[0]))
#         color_cycle = plt.rcParams['axes.prop_cycle'].by_key()['color']
        # print("color_cycle", color_cycle)
        plt.rcParams.update({'font.size': 25}) # 25 for 36x21 fig, 16 for 24x14 fig.
        # 36x21 for better resolution but about 900kb file size, 24x14 for okay resolution and 550kb file size
        fig, ax = plt.subplots(nrows=nrows_, ncols=ncols_, figsize=(7 * ncols_, 5 * nrows_))
        ax = np.atleast_2d(ax)
        # metrics_reshaped_squeezed = np.squeeze(metrics_reshaped)
        # print(np.squeeze(metrics_reshaped).shape)
        for i in range(len(self.final_rows_for_a_config)):
            i_index = i//(nseeds_ * ncols_) # = num_seeds * shape of more frequently changing hyperparam
            j_index = (i//nseeds_) % ncols_ #
            if i == 0:
                to_plot_ = stats_data[0:self.final_rows_for_a_config[i]+1, metric_num]
                to_plot_x = stats_data[0:self.final_rows_for_a_config[i]+1,-3]
            else:
                to_plot_ = stats_data[self.final_rows_for_a_config[i-1]+1:self.final_rows_for_a_config[i]+1, metric_num]
                to_plot_x = stats_data[self.final_rows_for_a_config[i-1]+1:self.final_rows_for_a_config[i]+1, -3]
            # print(to_plot_[-1])
        #     if i % 10 == 0:
        #         fig = plt.figure(figsize=(12, 7))
        #     print(i//50, (i//10) % 5)
            ax[i_index][j_index].plot(to_plot_x, to_plot_, rasterized=False)#, label="Seq len" + str(seq_lens[i//10]))
            if i % nseeds_ == nseeds_ - 1: # 10 is num. of seeds
        #         pass
        #         print("Plot no.", i//10)
                ax[i_index][j_index].set_xlabel("Train Timesteps")
                ax[i_index][j_index].set_ylabel("Reward")
        #         ax[i_index][j_index].set_title('Delay ' + str(delays[i_index]) + ', Sequence Length ' + str(sequence_lengths[j_index]))
                if len(self.dims_varied) > 1:
                    title_1st_dim = self.config_names[self.dims_varied[0]] + ' ' + str(self.dims_values[self.dims_varied[0]][i_index])
                    title_2nd_dim = self.config_names[self.dims_varied[1]] + ' '  + str(self.dims_values[self.dims_varied[1]][j_index])
                else:
                    title_1st_dim = self.config_names[self.dims_varied[0]] + ' ' + str(self.dims_values[self.dims_varied[0]][j_index])
                    title_2nd_dim = ''
                ax[i_index][j_index].set_title(title_1st_dim + ', ' + title_2nd_dim)
        #         ax[i_index][j_index].set_title('Sequence Length ' + str(seq_lens[j_index]))
        #         ax[i_index][j_index].set_title('Reward Density ' + str(reward_densities[j_index]))

        #         plt.legend(loc='upper left', prop={'size': 26})
        fig.tight_layout()
        # plt.suptitle("Training Learning Curves")
        plt.show()
        if save_fig:
            fig.savefig(self.stats_file.split('/')[-1] + ('_train' if train else '_eval') + '_learning_curves_' + str(self.metric_names[metric_num]) + '.pdf', dpi=300, bbox_inches="tight") # Generates high quality vector graphic PDF 125kb; dpi doesn't matter for this
