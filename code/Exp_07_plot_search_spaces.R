# Exp 07: Plot aspects of the search spaces. 
# create 1 bar plot and 2 box plots showing aspects of the 
# number of letter selectors by size of the characters in the 
# letter selector

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

# get the search space
sql <- 'select * from exp_02_search_space_size;'
ss_df <- RSQLite::dbGetQuery(conn=db_conn, statement = sql)
ss_df <- data.table(ss_df)
head(ss_df)

##
# GET THE NUMBER OF LETTER SELECTORS BY NUMBER OF CHARACTERS
##

n_letter_selectors_df <- ss_df[, .(n_letter_selectors = .N), by = .(ls_nchar_iter)]
# make a label!
n_letter_selectors_df[, cool_label := paste0(ls_nchar_iter, "\n(", comma(n_letter_selectors), ")")]
head(n_letter_selectors_df)

# 15 and 16 seem to have the same counts. What's up with that?
n15 <- unique(x = ss_df[ls_nchar_iter == 15, letter_selector])
n16 <- unique(x = ss_df[ls_nchar_iter == 16, letter_selector])

n_inter1516 <- base::setdiff(x = n15, y = n16)
n_inter1516

n_inter1615 <- base::setdiff(x = n16, y = n15)
n_inter1615
# the letter selectors are effectively the same.


##
# PLOT THE NUMBER OF LETTER SELECTORS BY NUMBER OF CHARACTERS IN THE LETTER SELECTOR
##

my_y_labels <- comma(10 ^ seq(0, 6))

my_plot <- ggplot(data = n_letter_selectors_df,
                  mapping = aes(x = ls_nchar_iter, y = log10(n_letter_selectors), color = 'grey', fill = 'red')) +
  geom_bar(stat="identity") +
  ggtitle(label = 'Number of letter selectors by number of characters in the letter selector') +
  scale_x_discrete(name = 'Number of characters in the letter selector (number of letter selectors)',
                   breaks = seq(1,16),
                   labels = n_letter_selectors_df$cool_label,
                   limits = factor(seq(1,16))) +
  scale_y_continuous(name = 'Number of letter selectors',
                     breaks = seq(0, 6),
                     labels = my_y_labels,
                     limits = c(0,6)) + 
  theme_bw() + 
  theme(strip.background = element_rect(fill = 'white'), legend.position = "none")

file_name <- 'ls_01_n_letter_selectors.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 1920, height = 960, res = 200)
plot(my_plot)
dev.off()

##
# PLOT THE NUMBER OF LOOKUPS BY NUMBER OF CHARACTERS IN THE LETTER SELECTOR
##

my_y_labels <- comma(10 ^ seq(0, 5))

my_plot <- ggplot(data = ss_df, mapping = aes(x = ls_nchar_iter, y = log10(ls_count), group = ls_nchar_iter)) +
  geom_boxplot(outlier.color =  "#646464", outlier.size = .5, outlier.shape = 19, outlier.alpha = .25) +
  ggtitle(label = 'Number of lookups by number of characters in the letter selector') +
  scale_x_discrete(name = 'Number of characters in the letter selector (number of letter selectors)',
                   breaks = seq(1,16),
                   labels = n_letter_selectors$cool_label,
                   limits = factor(seq(1,16))) +
  scale_y_continuous(name = 'Number of lookups',
                   breaks = seq(0, 5),
                   labels = my_y_labels,
                   limits = c(0,5)) + 
  theme_bw() + 
  theme(strip.background = element_rect(fill = 'white'), legend.position = "none")

file_name <- 'ls_02_n_lookups.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 1920, height = 960, res = 200)
plot(my_plot)
dev.off()

##
# PLOT THE NUMBER OF ITEMS IN THE LETTER SELECTORS BY NUMBER OF CHARACTERS IN THE LETTER SELECTOR
##

my_y_labels <- comma(10 ^ seq(0, 6))

my_plot <- ggplot(data = ss_df, mapping = aes(x = ls_nchar_iter, y = log10(n_search_space), group = ls_nchar_iter)) +
  geom_boxplot(outlier.color =  "#646464", outlier.size = .5, outlier.shape = 19, outlier.alpha = .25) +
  ggtitle(label = 'Number of elements in the letter selctor by number of characters in the letter selector') +
  scale_x_discrete(name = 'Number of characters in the letter selector (number of letter selectors)',
                   breaks = seq(1,16),
                   labels = n_letter_selectors$cool_label,
                   limits = factor(seq(1,16))) +
  scale_y_continuous(name = 'Number of elements in the letter selctor',
                     breaks = seq(0, 6),
                     labels = my_y_labels,
                     limits = c(0,6)) + 
  theme_bw() + 
  
  theme(strip.background = element_rect(fill = 'white'), legend.position = "none")

file_name <- 'ls_03_letter_selector_size.png'
fpn <- file.path(output_path, file_name)

png(filename = fpn, width = 1980, height = 960, res = 200)
plot(my_plot)
dev.off()
