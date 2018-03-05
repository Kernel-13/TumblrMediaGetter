import requests
import os
import time
from colorama import Fore, Style, init
init(convert=True)
from pathlib import Path
import logging
logging.basicConfig(handlers=[logging.FileHandler('activity_log.txt', 'w', 'utf-8')],level=logging.DEBUG)

def save_file(file_path, data):
    file = Path(file_path)
    filename = file_path.rsplit('\\', 1)[1]
    if not file.exists():
        with open(file_path, 'wb') as f:
            f.write(data.content)
            print(Fore.GREEN + 'Downloaded ' + filename)
            logging.info('File ' + filename + ' has been successfully saved at ' + file_path.replace(filename, ''))
    else:
        print(Fore.CYAN + 'File ' + filename + ' already exists')
        logging.info('File already exists: ' + os.getcwd() + '\\' + file_path)

def download_media(post, path, mediaType):
    file_path = ''
    media_url = ''
    content = None
    if mediaType == 'audio':    
        audio_url = post['audio_url'].rsplit('/', 1)[1]
        if '.mp3' in audio_url:
            media_url = post['audio_url']
            content = requests.get(media_url, stream=True)
        else:
            redirected = requests.get(post['audio_url'], allow_redirects=True)
            content = requests.get(redirected.url, stream=True)
            media_url = content.url
            if 'soundcloud' in post['audio_url']:
                media_url = content.url.split('?Policy')[0]
    elif mediaType == 'photo':  
        for photo in post['photos']:
            content = requests.get(photo['original_size']['url'], stream=True) 
            file_path = generate_filepath(path, post, photo['original_size']['url'])
            save_file(file_path, content) 
        return
    elif mediaType == 'video':  
        try:
            content = requests.get(post['video_url'], stream=True) 
            media_url = post['video_url']
        except KeyError:
            print(Fore.RED + 'Failed to download video from ' + post['post_url'])
            logging.error("Post doesn't have a 'video_url' field: " + post['post_url'])
            return
    file_path = generate_filepath(path, post, media_url)
    save_file(file_path, content)

def generate_filepath(path, post, media_url):
    extension = media_url.rsplit('.', 1)[1]
    photo_number = ''
    if 'photo' in path:
        photo_number = ' [' + media_url.replace('_',' ').split(' ')[1].rsplit('o', 1)[1] + ']'
    return path + '\\' + str(post['timestamp']) + ' ' + str(post['id']) + photo_number + '.' + extension
    
def get_posts(blog_name, media_type, tag=''):
    
    if tag != '': tag = '&tag=' + tag
    blog_url = 'https://api.tumblr.com/v2/blog/' + blog_name + '.tumblr.com/posts/' + media_type + '?api_key=zEhk20rj71veq1vOkr7wZ5HoRSOuwRunDR7ErNhoMePhIiOlit' + tag
    offset = 0
    folder_path = None
    while True:
        url = blog_url + "&offset=" + str(offset)        
        response = requests.get(url).json()
        
        if response['meta']['status'] == 200:
                        
            total_posts = response['response']['total_posts']
            if total_posts > 0:
                folder_path = blog_name + '\\' + media_type
                os.makedirs(folder_path, exist_ok=True)             
            elif total_posts == 0:
                if tag != '':
                    logging.warning('No ' + media_type + ' posts with tag = "' + tag.split('=')[1] + '" were found at ' + blog_name)
                    print(Fore.LIGHTMAGENTA_EX + "\nIt seems this blog doesn't contain any " + media_type + ' posts with the "' + tag.split('=')[1] + '" tag!')
                    print("Try another option or try a different blog / tag")
                else:
                    logging.warning('No ' + media_type + ' posts were found at ' + blog_name)
                    print(Fore.LIGHTMAGENTA_EX + "\nIt seems this blog doesn't contain any " + media_type + ' posts!')
                    print("Try another option or try a different blog")
                break
            
            for post in response['response']['posts']:
                download_media(post,folder_path,media_type)
                
            offset += 20
            
            if offset > total_posts:
                logging.info('All ' + media_type + ' posts from ' + blog_name + ' with tag "' + tag.split('=')[1] + '" have been downloaded')
                print('\nDone!')
                break
            
        elif response['meta']['status'] == 404:
            print(Fore.RED + "\nWe couldn't find any blog with that name.")
            print(Fore.RED + "Check the spelling of the name or try a different blog")
            logging.warning('Blog not found: ' + blog_name)
            break
        else:
            print(Fore.RED + "\nOops! We may have reached the rate limit. Try again in a couple of hours")
            logging.error('Server returned status ' + str(response['meta']['status']))
            logging.error(str(response['meta']['msg']))
            break

def tumblr_media_getter():
    media_types = {1:'photo', 2:'video',3:'audio' }
    while True:
        print('\nTumblr Media Getter v1.07')
        print('----------------------')
        print('Select an option:')
        print('1. Get Photos from a blog')
        print('2. Get Videos from a blog')
        print('3. Get Audio from a blog')
        print('0. Exit')
        data = input('Option: ')

        try:
            option = int(data)
            if option == 0:
                print(Fore.YELLOW + '\nGoodbye!')
                logging.info('User exited through the app menu')
                time.sleep(1)
                break
            elif option > 0 and option < 4:
                blog_name = input("Enter blog name: ")
                tag = input("Download posts that match the following tag (leave empty to download all posts): ")
                get_posts(blog_name.lower(), media_types[option],tag.lower())
            else:
                print(Fore.RED + "\nThat's not a valid option. Please try again")
        except ValueError:
            print(Fore.RED + "\nYou can only enter numbers. Please try again")

        print(Style.RESET_ALL)

def main():  
    logging.info('Starting application')    
    while True:
        try:
            tumblr_media_getter()
            break
        except KeyboardInterrupt:
            print(Style.RESET_ALL)
            logging.warning('SIGINT detected -- Waiting for user input')
            reply = input("You pressed Ctrl+Z. Do you want to exit the application? (Y/N): ")
            logging.warning('User reply to warning: ' + reply)
            if reply.lower().startswith('y'):
                break
         
if __name__== "__main__":
    main()