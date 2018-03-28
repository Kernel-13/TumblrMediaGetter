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
    if not file.exists() or os.path.getsize(file_path) != len(data.content):
        with open(file_path, 'wb') as f:
            f.write(data.content)
            print(Fore.GREEN + 'Downloaded ' + filename)
            logging.info('    File ' + filename + ' has been successfully saved at ' + file_path.replace(filename, ''))
    else:
        print(Fore.CYAN + 'File ' + filename + ' already exists')
        logging.info('    File already exists: ' + os.getcwd() + '\\' + file_path)

def download_media(post, path):
    file_path = ''
    media_url = ''
    content = None
    if post['type'] == 'audio':    
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
    elif post['type'] == 'photo':  
        for photo in post['photos']:
            content = requests.get(photo['original_size']['url'], stream=True) 
            file_path = generate_filepath(path, post, photo['original_size']['url'])
            save_file(file_path, content) 
        return
    elif post['type'] == 'video':  
        try:
            content = requests.get(post['video_url'], stream=True) 
            media_url = post['video_url']
        except KeyError:
            print(Fore.RED + 'Failed to download video from ' + post['post_url'])
            logging.error("    Post doesn't have a 'video_url' field: " + post['post_url'])
            return
    file_path = generate_filepath(path, post, media_url)
    save_file(file_path, content)

def generate_filepath(path, post, media_url):
    extension = media_url.rsplit('.', 1)[1]
    photo_number = ''
    if post['type'] == 'photo':
        photo_number = ' [' + media_url.replace('_',' ').split(' ')[1].rsplit('o', 1)[1] + ']'
    return path + '\\' + str(post['timestamp']) + ' ' + str(post['id']) + photo_number + '.' + extension
    
def get_posts(rqst_prmts):

    blog_url = 'https://api.tumblr.com/v2/blog/' + \
                rqst_prmts['blog_name'] + \
                '.tumblr.com/posts' 
    
    if rqst_prmts['single_post']:
        blog_url +=  '?id=' + rqst_prmts['post_id'] + \
                '&api_key=' + rqst_prmts['api_key']
        rqst_prmts['type'] = 'single posts'
    else:
        blog_url +=  '/' + rqst_prmts['type'] + \
                '?api_key=' + rqst_prmts['api_key']
        if rqst_prmts['tag']: 
            blog_url += '&tag=' + rqst_prmts['tag']
    
    offset = 0
    url = blog_url + "&offset=" + str(offset)        
    response = requests.get(url).json()
    
    if response['meta']['status'] == 200:
        total_posts = response['response']['total_posts']
        logging.info('    Nº of posts found: ' + str(total_posts))
                
        if total_posts > 0 and response['response']['posts']:
            print(Fore.GREEN + "\n========> Found " + str(total_posts) + " post(s)\n")
            folder_path = rqst_prmts['blog_name'] + '\\' + rqst_prmts['type']
            os.makedirs(folder_path, exist_ok=True)  
            
            while offset <= total_posts:
                for post in response['response']['posts']:  
                    download_media(post,folder_path)
                offset += 20
                url = blog_url + "&offset=" + str(offset)        
                response = requests.get(url).json()
            logging.info('    All post(s) downloaded successfully')
            print('\n     Done!')
                     
        elif total_posts == 0 or not response['response']['posts']:
            if not rqst_prmts['tag']:
                logging.warning('    No ' + rqst_prmts['type'] + ' posts were found at ' + rqst_prmts['blog_name'])
                print(Fore.LIGHTMAGENTA_EX + "\nIt seems this blog doesn't contain any " + rqst_prmts['type'] + ' posts!')
                print("Try another option or try a different blog")
            else:
                logging.warning('    No ' + rqst_prmts['type'] + ' posts with tag = "' + rqst_prmts['tag'] + '" were found at ' + rqst_prmts['blog_name'])
                print(Fore.LIGHTMAGENTA_EX + "\nIt seems this blog doesn't contain any " +rqst_prmts['type'] + ' posts with the "' + rqst_prmts['tag'] + '" tag!')
                print("Try another option or try a different blog / tag")
                
    elif response['meta']['status'] == 404:
        if rqst_prmts['single_post']:
            print(Fore.RED + "\nWe couldn't find any post with that ID (" + rqst_prmts['post_id'] + ").")
            print(Fore.RED + "Check the spelling of the name of the blog or try with a different post ID")
            logging.warning("    Unable to find post with ID " + rqst_prmts['post_id'] + " - Invalid POST ID or BLOG")
        else:
            print(Fore.RED + "\nWe couldn't find any blog with that name.")
            print(Fore.RED + "Check the spelling of the name or try a different blog")
            logging.warning('    Blog not found: ' + rqst_prmts['blog_name'])
        
    else:
        print(Fore.RED + "\nOops! We may have reached the rate limit. Try again in a couple of hours")
        logging.error('Server returned status ' + str(response['meta']['status']))
        logging.error(str(response['meta']['msg']))

def tumblr_media_getter():
    media_types = {1:'photo', 2:'video',3:'audio' }
    request_parameters = {'blog_name':'',
                          'api_key':'zEhk20rj71veq1vOkr7wZ5HoRSOuwRunDR7ErNhoMePhIiOlit',
                          'type': '',
                          'post_id':'',
                          'tag':'',
                          'single_post':''}
    while True:
        print('\nTumblr Media Getter v1.35')
        print('----------------------')
        print('Select an option:')
        print('1. Get Photos from a blog')
        print('2. Get Videos from a blog')
        print('3. Get Audio from a blog')
        print('4. Get media from a single post')
        print('0. Exit')
        data = input('Option: ')

        try:
            option = int(data)
            if option == 0:
                print(Fore.YELLOW + '\nGoodbye!')
                logging.info('    User exited through the app menu')
                time.sleep(1)
                break
            elif option > 0 and option < 5:
                request_parameters['blog_name'] = input("Enter blog name: ")
                if option == 4:
                    request_parameters['post_id'] = input("Enter post ID:  ")
                    request_parameters['single_post'] = True
                else:
                    request_parameters['tag'] = input("Download posts that match the following tag (leave empty to download all posts): ")
                    request_parameters['type'] = media_types[option]
                    request_parameters['single_post'] = False
                
                logging.info('    Starting web scraping with the following parameters:')
                for key, value in request_parameters.items():
                    logging.info('        ' + key + ': ' + str(value))
                    
                get_posts(request_parameters)
                request_parameters = request_parameters.fromkeys(request_parameters)
                request_parameters['api_key'] = 'zEhk20rj71veq1vOkr7wZ5HoRSOuwRunDR7ErNhoMePhIiOlit'
            else:
                print(Fore.RED + "\nThat's not a valid option. Please try again")
        except ValueError:
            print(Fore.RED + "\nYou can only enter numbers. Please try again")

        print(Style.RESET_ALL)

def main():  
    logging.info('    Starting application')    
    while True:
        try:
            tumblr_media_getter()
            break
        except KeyboardInterrupt:
            print(Style.RESET_ALL)
            logging.warning('    SIGINT detected -- Waiting for user input')
            reply = input("You pressed Ctrl+Z. Do you want to exit the application? (Y/N): ")
            logging.warning('    User reply to warning: ' + reply)
            if reply.lower().startswith('y'):
                break
         
if __name__== "__main__":
    main()
    