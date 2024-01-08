import json
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from modules.logger import logger


async def save_jobs_to_file(scheduler: AsyncIOScheduler, filePath: Path):
    jobs_data = []
    for job in scheduler.get_jobs():

        job_data = {
            'id': job.id,
            'end_date': job.args[-1].strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'data': job.args[-2],
        }
        jobs_data.append(job_data)
    logger.info(f"Stored {len(jobs_data)} schedules to load on server start.")
    with open(filePath, 'w') as file:
        json.dump(jobs_data, file)


async def send_message_job(bot: Client, client: Client, ad_message, channel_id, data, end_date):
    media_group = []
    try:
        if 'media_group' in ad_message:
            logger.warning(f"Attempting to send media group")
            media_group = ad_message['media_group']
            media_data = []
            for media_item in media_group:
                if media_item['type'] == 'photo':
                    file_id = media_item['media']
                    loaded_media_data = await bot.download_media(file_id, in_memory=True)
                    media_data.append(InputMediaPhoto(
                        media=loaded_media_data, caption=media_item['caption']))
                elif media_item['type'] == 'video':
                    file_id = media_item['media']
                    loaded_media_data = await bot.download_media(file_id, in_memory=True)
                    media_data.append(InputMediaVideo(
                        media=loaded_media_data, caption=media_item['caption']))

            await client.send_media_group(channel_id, media_data)

        elif 'vid' in ad_message:
            logger.warning(f"Attempting to send video")
            video_data = await bot.download_media(ad_message['vid'], in_memory=True)
            await client.send_video(channel_id, video_data, caption=ad_message['text'])
        elif 'img' in ad_message:
            logger.warning(f"Attempting to send image")
            photo_data = await bot.download_media(ad_message['img'], in_memory=True)
            await client.send_photo(channel_id, photo_data, caption=ad_message['text'])
        elif 'text' in ad_message:
            await client.send_message(channel_id, ad_message['text'])

        # logger.info(
        #     f' ✔️✔️✔️ FROM {client.api_id} to channel {channel_id}')
    except Exception as e:
        logger.error(str(e))
        logger.error(f"PROBLEM WITH {client.api_id} sending to {channel_id}")
