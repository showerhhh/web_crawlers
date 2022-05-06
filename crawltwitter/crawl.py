import datetime
import os

import arrow
import stweet as st


def search_entry(key_words, start_date, end_date, daysdelta=1):
    # 左闭右开区间（不包括最后一天）
    path = f'./{key_words}/'
    if not os.path.exists(path):
        os.makedirs(path)

    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

    crawl_start = start_date
    while crawl_start < end_date:
        start_str = crawl_start.strftime('%Y-%m-%d')
        crawl_end = crawl_start + datetime.timedelta(days=daysdelta)
        if crawl_end > end_date:
            crawl_end = end_date
        end_str = crawl_end.strftime('%Y-%m-%d')
        try_search(key_words, start_str, end_str)
        crawl_start = crawl_end
        crawl_end += datetime.timedelta(days=daysdelta)


def try_search(key_words, time_start, time_end):
    # 示例：try_search(key_words='#covid19', time_start='2022-01-1', time_end='2022-01-2'
    # 左闭右开区间（不包括最后一天）
    tweets_file_path = f'./{key_words}/{time_start}_{time_end}_tweet.json'
    user_file_path = f'./{key_words}/{time_start}_{time_end}_user.json'
    if os.path.exists(tweets_file_path):
        print(f'key_words={key_words}, time_start={time_start}, time_end={time_end} 已抓取！')
        return
    output_jl_tweets = st.JsonLineFileRawOutput(tweets_file_path)
    output_jl_users = st.JsonLineFileRawOutput(user_file_path)
    output_print = st.PrintRawOutput()
    search_tweets_task = st.SearchTweetsTask(
        all_words=key_words,
        since=arrow.get(time_start),
        until=arrow.get(time_end),
    )
    runner = st.TweetSearchRunner(
        search_tweets_task=search_tweets_task,
        tweet_raw_data_outputs=[output_print, output_jl_tweets],
        user_raw_data_outputs=[output_print, output_jl_users]
    )
    runner.run()


def try_user_scrap():
    user_task = st.GetUsersTask(['SteveDaines'])  # screen_name去掉前面的@
    output_json = st.JsonLineFileRawOutput('output_raw_user.jl')
    output_print = st.PrintRawOutput()
    runner = st.GetUsersRunner(
        get_user_task=user_task,
        raw_data_outputs=[output_print, output_json]
    )
    runner.run()


if __name__ == '__main__':
    key_words = '#covid19'
    start_date = '2021-01-01'
    end_date = '2022-01-01'
    search_entry(key_words, start_date, end_date)
