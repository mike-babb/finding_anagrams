# mike babb
# visualize aspects of the different anagram processing techniques

##
# clean up
##
rm(list = ls())
gc()

library(data.table)
library(ggplot2)
library(magrittr)
library(RSQLite)
library(stringi)
library(RColorBrewer)


# input db path and name
db_path <- '/project/finding_anagrams/db'
db_name <- 'words.db'
db_path_name <- file.path(db_path, db_name)

# output directory
output_path <- '/project/finding_anagrams/graphics'
if(!dir.exists(output_path)){
  dir.create(output_path)
}


####
# PART 1: LOAD DATA FROM SQLITE
####
# build the connection
sqlite <- RSQLite::dbDriver('SQLite')
db_conn <- RSQLite::dbConnect(drv=sqlite, dbname=db_path_name,  flags = RSQLite::SQLITE_RO)

keep_col_names <- c('word', 'lcase', 'n_chars', 'first_letter', 'word_group_id', 'n_seconds', 'matrix_extraction_option', 'word_processed')

# use a simple loop to load data from the SQLite tables
base_sql <- 'select * from table_name;'
df_list <- list()
for(tn in seq(1, 5)){
  table_name <- paste0('words_me_', stri_pad(str=tn, width = 2, pad = '0'))
  
  sql <- stri_replace_all_fixed(str = base_sql, pattern = 'table_name', replacement = table_name)
  print(sql)

  # send a query to a database, return the result as a dataframe  
  df <- RSQLite::dbGetQuery(conn=db_conn, statement = sql)
  
  df <- data.table(df)
  

  df <- df[, ..keep_col_names]
  df <- df[word_processed == 1, ]
  
  # colnames(df) <- rename_col_names
  
  
  df_list[[tn]] <- df
}

# let's also load data featuring the search space
sql <- 'select * from words_me_05'
sdf <- RSQLite::dbGetQuery(conn=db_conn, statement = sql)
sdf <- data.table(sdf)

# keep only the following columns
keep_col_names <- c('word', 'lcase', 'n_chars', 'first_letter', 'word_group_id', 'word_processed', 
                    'full_matrix_lookup', 'n_char_lookup', 'first_letter_lookup',
                    'single_letter_lookup', 'letter_selector_lookup',
                    'nc_ls_lookup')

sdf <- sdf[word_processed == 1, ..keep_col_names]



# disconnect
RSQLite::dbDisconnect(conn=db_conn)

# create a datatable
df <- rbindlist(l= df_list)
proc_time_df <- df[, .(tot_seconds = sum(n_seconds)),
                   by = (matrix_extraction_option)]
proc_time_df[, tot_minutes := tot_seconds / 60]


####
# PART 2: SHAPE DATA TO PLOT TOTAL PROCESSING TIME BY LETTER
####
# specify factor levels
my_factor_levels <- df$matrix_extraction_option %>% unique() %>% sort(decreasing = TRUE)
my_factor_labels <- stri_pad(str=my_factor_levels, width = 2, pad = '0')
df[, me_factor := factor(x=matrix_extraction_option, levels = my_factor_levels, labels = my_factor_labels)]


head(df)

# aggregate to get total processing time by letter and other summary stats
df_agg <- df[, .(word_count = .N,
                 tot_proc_time = sum(n_seconds),
                 mean_proc_time = mean(n_seconds),
                 med_proc_time = median(n_seconds)),
             by = .(n_chars, matrix_extraction_option, me_factor)]

# reorder, just for inspection
df_agg <- df_agg[order(n_chars, me_factor)]
# compute minutes
df_agg[, tot_proc_time_minutes := tot_proc_time / 60]
summary(df_agg$tot_proc_time)

# get the total time per matrix_extraction_option, this will be inserted into the legend
tt_df <- df_agg[, .(tot_proc_time_minutes = sum(tot_proc_time_minutes)),
            by = .(me_factor)]

# format the string
tt_df[, nice_label_format := paste0(me_factor, '\n(', round(tot_proc_time_minutes, 0), ' minutes)')]
tt_df %>% head()

####
# PART 3: POINT AND LINE PLOT OF TOTAL TIME PER LETTER BY TECHNIQUE
####

# select colors. This needs to be consistent across graphs version 1 and 2
my_colors <- RColorBrewer::brewer.pal(n=5, name = 'Dark2')

#base::rev(RColorBrewer::brewer.pal(n=5, name = 'Dark2'))[2:5]
#base::rev(RColorBrewer::brewer.pal(n=5, name = 'Dark2'))


# set breaks and format the y-axis
df_agg$tot_proc_time_minutes %>% summary()

max_minutes <- ceiling(max(df_agg$tot_proc_time_minutes))
y_breaks <- seq(0, max_minutes, 5)

if(y_breaks[length(y_breaks)] < max_minutes){
  y_breaks <- c(y_breaks, y_breaks[length(y_breaks)] + 5)
}


y_labels <- formatC(x = y_breaks, digits = 0, format = 'f',big.mark = ',')
y_limits <- range(y_breaks)

# make the plot
my_plot <- ggplot(data=df_agg, aes(x=n_chars, y = tot_proc_time_minutes, color = me_factor)) +
  geom_line(linewidth = 1.5) + 
  geom_point(size = 2) +
  ggtitle(label = 'Total Time To Find Anagrams By Word Length And Processing Technique') +
  scale_color_manual(values = my_colors, labels = tt_df$nice_label_format) + 
  scale_x_discrete(name = 'Word length (# of Characters)',
                   breaks = seq(1,max(df_agg$n_chars)),
                   labels = factor((seq(1,max(df_agg$n_chars)))),
                   limits = factor(seq(1, max(df_agg$n_chars)))) +
  scale_y_continuous(name = 'Total Processing time (minutes)',
                     breaks = y_breaks,
                     labels = y_labels,
                     limits = y_limits) +
  guides(color = guide_legend(title = 'Processing\nTechnique\n(total time)')) +
  theme_bw()
# check plot

# save plot to disk
file_name <- 'tot_proc_time_by_word_length_v2.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()

####
# PART 4: POINT AND LINE PLOT OF AVERAGE PROCESSING TIME PER LETTER BY TECHNIQUE
####

max_avg_seconds <- df_agg$mean_proc_time %>% max()
max_avg_seconds
max_avg_seconds <- 0.07

y_breaks = seq(0, max_avg_seconds, .01)
y_labels <- formatC(x = y_breaks, digits = 2, format = 'f', big.mark = ',')
y_limits <- range(y_breaks)

my_plot <- ggplot(data=df_agg, aes(x=n_chars, y = mean_proc_time, color = me_factor)) +
  geom_point(size=1.5) + 
  geom_line(linewidth=2) +
  ggtitle(label = 'Average Time To Find Anagrams By Word Length And Processing Technique') +
  scale_color_manual(values = my_colors) + 
  scale_x_discrete(name = 'Word length (# of Characters)',
                   breaks = seq(1,max(df_agg$n_chars)),
                   labels = factor((seq(1,max(df_agg$n_chars)))),
                   limits = factor(seq(1, max(df_agg$n_chars)))) +
  scale_y_continuous(name = 'Average Processing time (seconds)',
                     breaks = y_breaks,
                     labels = y_labels,
                     limits = y_limits) +
  guides(color = guide_legend(title = 'Processing\nTechnique')) +
  theme_bw()

file_name <- 'avg_proc_time_by_word_length_v2.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()

####
# PART 5: POINT AND LINE PLOT OF THE AVERAGE NUMBER OF SEARCH CANDIDATES BY WORD LENGTH AND TECHNIQUE
####

head(sdf)
# melt
melt_sdf <- melt(data = sdf, id.vars = c('word', 'word_group_id', 'lcase', 'n_chars', 'first_letter',
                                         'word_processed'),
                 variable.name = 'matrix_extraction_option',
                 value.name = 'n_candidates',
                 variable.factor = FALSE
                 )

head(melt_sdf)

my_values <- sort(unique(melt_sdf$matrix_extraction_option))
my_values
my_factor_labels <- c('ME 03: First Letter',
                      'ME 01: Full Matrix',
                      'ME 04: Letter Selector',
                      'ME 02: Word Length',
                      'ME 05: Word Length & Letter Selector',
                      'ME 06: Focal Letter')
search_df_labels <- data.frame( matrix_extraction_option = my_values)
search_df_labels <- data.table(search_df_labels)
search_df_labels[, matrix_extraction_option_labels := my_factor_labels]

search_df_labels <- search_df_labels[order(matrix_extraction_option_labels), ]
search_df_labels[, matrix_extraction_option_factor := factor(x = matrix_extraction_option_labels,
                                                             levels = matrix_extraction_option_labels,
                                                             labels = matrix_extraction_option_labels)]



melt_sdf <- merge(x = melt_sdf, y = search_df_labels)

melt_sdf_agg <- melt_sdf[, .(mean_comp_words = mean(n_candidates)),
                       by = .(n_chars, matrix_extraction_option_labels, matrix_extraction_option_factor)]


y_breaks <- seq(0, 225000, 25000)
y_labels <- formatC(x = y_breaks, digits = 0, format = 'f',big.mark = ',')
y_limits <- range(y_breaks)

my_colors <- RColorBrewer::brewer.pal(n=6, name = 'Dark2')

my_plot <- ggplot(data=melt_sdf_agg, aes(x=n_chars, y = mean_comp_words, color = matrix_extraction_option_factor)) +
  geom_point(size=1.5) + 
  geom_line(linewidth=2) +
  ggtitle(label = 'Average Number of Candidate Words By Word Length And Processing Technique') +
  scale_color_manual(values = my_colors) + 
  scale_x_discrete(name = 'Word length (# of Characters)',
                   breaks = seq(1,max(melt_sdf_agg$n_chars)),
                   labels = factor((seq(1,max(melt_sdf_agg$n_chars)))),
                   limits = factor(seq(1, max(melt_sdf_agg$n_chars)))) +
  scale_y_continuous(name = 'Average Number of Candidate Words',
                     breaks = y_breaks,
                     labels = y_labels,
                     limits = y_limits) +
  guides(color = guide_legend(title = 'Processing\nTechnique')) +
  theme_bw()
file_name <- 'avg_search_candidates_by_word_length_v2.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()

# do this now by first letter
melt_sdf_agg <- melt_sdf[, .(mean_comp_words = mean(n_candidates)),
                         by = .(first_letter, matrix_extraction_option_labels, matrix_extraction_option_factor)]


y_breaks <- seq(0, 225000, 25000)
y_labels <- formatC(x = y_breaks, digits = 0, format = 'f',big.mark = ',')
y_limits <- range(y_breaks)

my_colors <- RColorBrewer::brewer.pal(n=6, name = 'Dark2')

my_plot <- ggplot(data=melt_sdf_agg, aes(x=first_letter, y = mean_comp_words, group = matrix_extraction_option_factor,
                                         color = matrix_extraction_option_factor)) +
  geom_point(size=1.5) + 
  geom_line(linewidth=2) +
  ggtitle(label = 'Average Number of Candidate Words By First Letter And Processing Technique') +
  scale_color_manual(values = my_colors) + 
  scale_y_continuous(name = 'Average Number of Candidate Words',
                     breaks = y_breaks,
                     labels = y_labels,
                     limits = y_limits) +
  guides(color = guide_legend(title = 'Processing\nTechnique')) +
  theme_bw()
plot(my_plot)


file_name <- 'avg_search_candidates_by_first_letter_v2.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()


####
# PART 6: POINT AND LINE PLOT OF THE AVERAGE NUMBER OF FROM/TO WORDS BY WORD LENGTH, FACETED
####

# create a datatable

# aggregate to get averages
df_agg <- df[matrix_extraction_option == 4, .(mean_from_words = mean(n_from_words),
                 mean_to_words = mean(n_to_words)),
             by = .(n_chars)]
df_agg %>% tail()

# melt, then create groups
df_melt <- melt.data.table(data = df_agg, id.vars = 'n_chars', variable.name = 'word_stat',
                           value.name = 'value', variable.factor = FALSE)
df_melt %>% head()

# make factors
my_factor_levels <- df_melt$word_stat %>% unique() %>% sort()
# manually specify factor label ordering
my_factor_levels <- c("mean_from_words","mean_to_words")
my_factor_labels <- c('Avg. From Words', 'Avg. To Words')

df_melt[, word_stat_factor := factor(x=word_stat, levels = my_factor_levels, labels = my_factor_labels)]

##
# average number of from words by word length
##
df_melt$value %>% summary()
y_breaks <- seq(0, 70000, 10000)
y_labels <- formatC(x = y_breaks, digits = 0, format = 'f',big.mark = ',')
y_limits <- range(y_breaks)


my_plot <- ggplot(data=df_melt, aes(x=n_chars, y = value)) +
  geom_point(size=1.5) + 
  geom_line(size=2) +
  ggtitle(label = 'Average Number of From/To Words By Word Length') +
  scale_x_discrete(name = 'Word length (# of Characters)',
                   breaks = seq(1,max(df_agg$n_chars)),
                   labels = factor((seq(1,max(df_agg$n_chars)))),
                   limits = factor(seq(1, max(df_agg$n_chars)))) +
  scale_y_continuous(name = 'Average Number of From/To Words') +
  guides(color = guide_legend(title = 'From/To\nRelationship')) +
  theme_bw() +
  facet_grid(rows = vars(word_stat_factor), scales = 'free')
  
file_name <- 'avg_from_to_words_by_word_length_v2.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()


df_summary <- df[, as.list(summary(n_candidates)), by = matrix_extraction_option]


