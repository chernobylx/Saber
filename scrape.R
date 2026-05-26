library(baseballr)
library(dplyr)
library(readr)
library(lubridate)
library(future.apply)
library(doFuture)
library(reproducible)
library(progressr)

registerDoFuture()

tmpDir <- file.path(tempdir())
opts <- options(reproducible.cachePath = tmpDir)


scrape_statcast_schedules <- function(){
  for(year in 2015:2025){
    df <- mlb_schedule(season = year)
    write_csv(df, paste0('data/schedule/schedule_',year,'.csv'))
  }
}
#scrape_statcast_schedules()


scrape_pbp_season <- function(year){
  sched <- read_csv(paste0('data/schedule/schedule_',year,'.csv'), guess_max = Inf)
  #mlb throws an error for games that were cancelled
  sched <- sched |> filter(status_coded_game_state != "C" & status_coded_game_state != "D")
  pks <- sched$game_pk
  file <- paste0('data/pbp/pbp_',year,'.csv');

  N <- length(pks)
  p <- progressor(along = 1:N)
  registerDoFuture()
  plan(multisession(workers = 8))
  dfs <- foreach(i = 1:N, .options.future = list(seed = TRUE)) %dofuture% {
    p(message = i)
    Cache(mlb_pbp(pks[i]), verbose = 0, cachePath = tmpDir)
  }

  df <- bind_rows(dfs)
  write_csv(df, file)
}

with_progress(scrape_pbp_season(2021))


