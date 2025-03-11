# Mike Babb
# babb.mike@outlook.com
# Find anagrams
# Part 9: Plot aspects of timing


##
# clean up
##
rm(list = ls())
gc()

library(scales)
library(data.table)
library(ggplot2)
library(magrittr)
library(RSQLite)
library(RColorBrewer)
library(stringi)


# input db path and name
db_path <- '/project/finding_anagrams/data'
db_name <- 'words.db'
db_path_name <- file.path(db_path, db_name)

# output directory
output_path <- '/git/finding_anagrams/graphics'
if(!dir.exists(output_path)){
  dir.create(output_path)
}


####
# PART 1: LOAD DATA FROM SQLITE
####
# build the connection
sqlite <- RSQLite::dbDriver('SQLite')
db_conn <- RSQLite::dbConnect(drv=sqlite, dbname=db_path_name,  flags = RSQLite::SQLITE_RO)

# word groups
sql <- 'select * from word_groups;'
wg_df <- RSQLite::dbGetQuery(conn=db_conn, statement = sql)
wg_df <- data.table(wg_df)
head(wg_df)

# look up counts
sql <- 'select * from word_group_lookup_counts;'
wg_lu_df <- RSQLite::dbGetQuery(conn=db_conn, statement = sql)
wg_lu_df <- data.table(wg_lu_df)

# use a simple loop to load data from the processed word tables
base_sql <- 'select * from table_name;'
df_list <- list()
for(tn in seq(1, 6)){
  table_name <- paste0('words_me_', stri_pad(str=tn, width = 2, pad = '0'))
  
  sql <- stri_replace_all_fixed(str = base_sql, pattern = 'table_name', replacement = table_name)
  print(sql)

  # send a query to a database, return the result as a dataframe  
  df <- RSQLite::dbGetQuery(conn=db_conn, statement = sql)
  
  df <- data.table(df)

  df_list[[tn]] <- df
}

# disconnect
RSQLite::dbDisconnect(conn=db_conn)

# create a datatable: the timing and look up dataframes
# remove the reference to the previous dataframe
rm(df)
# gather all of the datatables
tdf <- rbindlist(l = df_list)
# check
head(tdf)
table(tdf$matrix_extraction_option)


####
# PROC TIME DF
####

proc_time_df <- tdf[, .(tot_seconds = sum(n_seconds)),
                   by = (matrix_extraction_option)]
proc_time_df[, tot_minutes := tot_seconds / 60]

####
# PART 2: SHAPE DATA TO PLOT TOTAL PROCESSING TIME BY LETTER
####

# specify factor levels
my_factor_levels <- tdf$matrix_extraction_option %>% unique() %>% sort(decreasing = FALSE)
# manually create factor labels
my_factor_labels <- c(
  'ME 01: Full Matrix',
  'ME 02: Word Length',
  'ME 03: First Letter',
  'ME 04: Single LC Letter',
  'ME 05: Three LC Letters',
  'ME 06: Word Length & Three LC Letters'
)

# this is the first use of the factor.
# factors are effectively categorical variables.
# but, there is an implicit ordering to the factor levels.
# you can create those levels, or R will do it for you.
# I like to manually create the levels so that I can better control the graphics.
tdf[, me_factor := factor(x=matrix_extraction_option, levels = my_factor_levels, labels = my_factor_labels)]
head(tdf)


tdf <- merge(x = tdf, y = wg_df[, .(word_group_id, n_chars)])

# aggregate to get total processing time by letter and other summary stats
df_agg <- tdf[, .(word_count = .N,
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
tt_df <- df_agg[, .(tot_proc_time = sum(tot_proc_time),
  tot_proc_time_minutes = sum(tot_proc_time_minutes)),
            by = .(me_factor)]

head(tt_df)

# format the string
tt_df[, nice_label_format := paste0(me_factor, '\n(', round(tot_proc_time_minutes, 0), ' minutes)')]
tt_df %>% head()

meo_count <- nrow(tt_df)

####
# PART 3: POINT AND LINE PLOT OF TOTAL TIME PER LETTER BY TECHNIQUE
####

# select colors. This needs to be consistent across graphs version 1 and 2
my_colors <- RColorBrewer::brewer.pal(n=meo_count, name = 'Dark2')

#base::rev(RColorBrewer::brewer.pal(n=5, name = 'Dark2'))[2:5]
#base::rev(RColorBrewer::brewer.pal(n=5, name = 'Dark2'))


# set breaks and format the y-axis
df_agg$tot_proc_time_minutes %>% summary()

max_minutes <- ceiling(max(df_agg$tot_proc_time_minutes))
y_breaks <- seq(0, max_minutes, 1)

if(y_breaks[length(y_breaks)] < max_minutes){
  y_breaks <- c(y_breaks, y_breaks[length(y_breaks)] + 1)
}

# check the breaks
y_breaks

y_labels <- formatC(x = y_breaks, digits = 0, format = 'f',big.mark = ',')
y_limits <- range(y_breaks)



# make the plot
my_plot <- ggplot(data=df_agg, aes(x=n_chars, y = tot_proc_time_minutes, color = me_factor)) +
  geom_line(linewidth = 1.5) + 
  geom_point(size = 2) +
  ggtitle(label = 'Total Time To Find Parent Words By Word Length And Processing Technique') +
  scale_color_manual(values = my_colors, labels = tt_df$nice_label_format) + 
  scale_x_discrete(name = 'Word length (# of Characters)',
                   breaks = seq(1,max(df_agg$n_chars)),
                   labels = factor((seq(1,max(df_agg$n_chars)))),
                   limits = factor(seq(1, max(df_agg$n_chars)))) +
  scale_y_continuous(name = 'Total Processing time (minutes)',
                     breaks = y_breaks,
                     labels = y_labels,
                     limits = y_limits) +
  guides(color = guide_legend(title = 'Matrix Extraction Technique\n(total time)')) +
  theme_bw()

# check the plot
my_plot

# save the plot disk
file_name <- 'wl_time_tot_proc_time.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()


####
# PART 4: POINT AND LINE PLOT OF AVERAGE PROCESSING TIME PER LETTER BY TECHNIQUE
####

max_avg_seconds <- df_agg$mean_proc_time %>% max()
max_avg_seconds
# let's set it to .05
max_avg_seconds <- .06

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

# check the plot
my_plot

# save the plot
file_name <- 'wl_time_avg_proc_time.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()

####
# PART 5: POINT AND LINE PLOT OF THE AVERAGE NUMBER OF SEARCH CANDIDATES BY WORD LENGTH AND TECHNIQUE
####

my_values <- sort(unique(tdf$matrix_extraction_option))
my_values
search_df_labels <- data.frame( matrix_extraction_option = my_values)
search_df_labels <- data.table(search_df_labels)
search_df_labels[, matrix_extraction_option_labels := my_factor_labels]

search_df_labels <- search_df_labels[order(matrix_extraction_option_labels), ]
search_df_labels[, matrix_extraction_option_factor := factor(x = matrix_extraction_option_labels,
                                                             levels = matrix_extraction_option_labels,
                                                             labels = matrix_extraction_option_labels)]

# melt the wg_lu_df 

# drop column names
col_names <- c("word_group_id","n_chars","me_01_full_matrix_lookup",
               "me_02_n_char_lookup","me_03_first_letter_lookup",
               "me_04_single_letter_lookup","me_05_letter_selector_lookup",
               "me_06_nc_ls_lookup")

wg_lu_df <- wg_lu_df[, ..col_names]

melt_wg_lu_df <- melt.data.table(data = wg_lu_df,
                                 id.vars = c('word_group_id',
                                             'n_chars'),
                                 variable.name = 'matrix_extraction_option_label',
                                 value.name = 'n_candidates',variable.factor = FALSE
                                  )
melt_wg_lu_df[, matrix_extraction_option := substr(x = matrix_extraction_option_label,
                                                   start = 5,stop = 5)]
melt_wg_lu_df[, matrix_extraction_option := as.integer(matrix_extraction_option)]
head(melt_wg_lu_df)

head(search_df_labels)

melt_wg_lu_df <- merge(x = melt_wg_lu_df, y = search_df_labels, by = c('matrix_extraction_option'))

melt_sdf_agg <- melt_wg_lu_df[, .(mean_comp_words = mean(n_candidates)),
                       by = .(n_chars, matrix_extraction_option_labels, matrix_extraction_option_factor)]


y_breaks <- seq(0, 225000, 25000)
y_labels <- formatC(x = y_breaks, digits = 0, format = 'f',big.mark = ',')
y_limits <- range(y_breaks)

my_colors <- RColorBrewer::brewer.pal(n=meo_count, name = 'Dark2')

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

my_plot

file_name <- 'wl_search_space_avg.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()

####
# PART 6: POINT AND LINE PLOT OF THE AVERAGE NUMBER OF FROM/TO WORDS BY WORD LENGTH, FACETED
####

# create a data.table

# aggregate to get averages
# pick a matrix extraction option - this part is all the same
tdf_agg <- tdf[matrix_extraction_option == 1, .(mean_from_words = mean(n_from_word_groups),
                 mean_to_words = mean(n_to_word_groups)),
             by = .(n_chars)]
tdf_agg %>% tail()

# melt to create groups for easier plotting
df_melt <- melt.data.table(data =tdf_agg, id.vars = 'n_chars', variable.name = 'word_stat',
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
  geom_line(linewidth=2) +
  ggtitle(label = 'Average Number of From/To Words By Word Length') +
  scale_x_discrete(name = 'Word length (# of Characters)',
                   breaks = seq(1,max(df_agg$n_chars)),
                   labels = factor((seq(1,max(df_agg$n_chars)))),
                   limits = factor(seq(1, max(df_agg$n_chars)))) +
  scale_y_continuous(name = 'Average Number of From/To Words', label = comma) +
  guides(color = guide_legend(title = 'From/To\nRelationship')) +
  theme_bw() +
  facet_grid(rows = vars(word_stat_factor), scales = 'free')

my_plot
  
file_name <- 'wl_from_to_words_avg.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()

####
# PART 7: Box and whisker plot of the distribution of from to words
#### 
# select meo 1, it doesn't matter which meo we use, all of the numbers are the sam
w_tdf <- tdf[matrix_extraction_option == 1, ]
head(w_tdf)
w_tdf$matrix_extraction_option %>% unique()

w_tdf$n_from_word_groups %>% summary()
w_tdf$n_to_word_groups %>% summary()

# melt, to make it make sense
melt_df = melt.data.table(data = w_tdf, id.vars = c('n_chars'),
                          measure.vars = c('n_from_word_groups', 'n_to_word_groups'),
                          variable.name = 'group_direction',value.name = 'word_groups',
                          value.factor = FALSE)
melt_df %>% head()

# remove values less than 99.5%
t_upper_bound <- quantile(x= w_tdf$n_to_word_groups, probs = .99999)
t_upper_bound

f_upper_bound <- quantile(x= w_tdf$n_from_word_groups, probs = .99999)
f_upper_bound

dim(melt_df)

#w_tdf <- w_tdf[n_to_word_groups <= upper_bound, ]
w_melt_df <- melt_df[word_groups <= t_upper_bound, ]
w_melt_df %>% dim()

y_breaks <- seq(0, 17000, 1000)
y_labels <- formatC(x = y_breaks, digits = 0, format = 'f',big.mark = ',')
y_limits <- range(y_breaks)

head(w_melt_df)

w_melt_df %>% head()
my_factor_levels <- c('n_from_word_groups', 'n_to_word_groups')
my_factor_labels <- c('From words', 'To words' )

w_melt_df[, group_direction_factor := factor(x = group_direction,
                                             levels = my_factor_levels,
                                             labels = my_factor_labels,
                                             ordered = TRUE)]


my_plot <- ggplot(data=w_melt_df, aes(x=n_chars, y = word_groups, group = n_chars)) +
  geom_boxplot() + 
  ggtitle(label = 'Number of Words By Word Length') +
  scale_x_discrete(name = 'Word length (# of Characters)',
                   breaks = seq(1,max(w_melt_df$n_chars)),
                   labels = factor((seq(1,max(w_melt_df$n_chars)))),
                   limits = factor(seq(1, max(w_melt_df$n_chars)))) +
  scale_y_continuous(name = 'Number of Words',breaks = y_breaks,
                     labels = y_labels) +
  
  theme_bw() + 
  facet_grid(rows = w_melt_df$group_direction_factor, scales = 'fixed')

my_plot

file_name <- 'wl_from_to_words_distribution.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()

####
# Part 8: Box and whisker plot of the distribution of search candidates for 2 - 6
####

wdf <- melt_wg_lu_df[, ]
head(wdf)

wdf$n_candidates %>% summary()

# remove values less than 99.5%

y_breaks <- seq(0, 220000, 20000)
y_labels <- formatC(x = y_breaks, digits = 0, format = 'f',big.mark = ',')
y_limits <- range(y_breaks)
y_labels

head(wdf)

my_plot <- ggplot(data=wdf, aes(x=n_chars, y = n_candidates, group = n_chars)) +
  geom_boxplot() + 
  ggtitle(label = 'Number of Candidates') +
  scale_x_discrete(name = 'Word length (# of Characters)',
                   breaks = seq(1,max(df_agg$n_chars)),
                   labels = factor((seq(1,max(df_agg$n_chars)))),
                   limits = factor(seq(1, max(df_agg$n_chars)))) +
  scale_y_continuous(name = 'Number of candidates', label = comma) +
  theme_bw()  +
  facet_grid(rows = vars(matrix_extraction_option_factor), scales = 'free')

my_plot


file_name <- 'wl_search_space_number_of_candidate_words.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 960, height = 720)
plot(my_plot)
dev.off()


####
# Part 9: Top five from/to words by word-length 
####

# let's join by the wdf and the w_tdf in order to get the top five

temp_tdf <- w_tdf[matrix_extraction_option == 1, .(word_group_id, n_from_word_groups, n_to_word_groups)]

temp_wg_df <- wg_df[, .(word_group_id, word, n_chars)]

out_df <- merge.data.table(x = temp_tdf, y = temp_wg_df)

out_df[, n_from_rank := frankv(x = n_from_word_groups,order = -1)]
out_df[, n_to_rank := frankv(x = n_from_word_groups, order = -1)]

head(out_df)










