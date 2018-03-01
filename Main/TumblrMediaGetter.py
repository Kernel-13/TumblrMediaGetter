import requests
import os
import time
from colorama import Fore, Style, init
init(convert=True)
from pathlib import Path
import logging
logging.basicConfig(filename='activity_log.txt', filemode='w',level=logging.DEBUG)

def writeFile(finalPath, finalUrl):
    file = Path(finalPath)
    fileName = finalPath.rsplit('\\', 1)[1]
    if not file.exists():
        with open(finalPath, 'wb') as f:
            f.write(finalUrl.content)
            print(Fore.GREEN + 'Downloaded ' + fileName)
            logging.info('File ' + fileName + ' has been successfully saved at ' + finalPath.replace(fileName, ''))
    else:
        print(Fore.CYAN + 'File ' + fileName + ' already exists')
        logging.info('File already exists: ' + os.getcwd() + '\\' + finalPath)

def generatePath(path, timestamp, tumblrFileUrl):
    name = ''
    extension = tumblrFileUrl.rsplit('.', 1)[1]
    if 'Pictures' in path:
        name = '_p' + tumblrFileUrl.replace('_',' ').split(' ')[1].rsplit('o', 1)[1]
    return path + '\\' + str(timestamp) + name + '.' + extension

def getPictures(post, path):  
    for photo in post['photos']:
        url = requests.get(photo['original_size']['url'], stream=True) 
        picName = generatePath(path, post['timestamp'], photo['original_size']['url'])
        writeFile(picName, url)   
     
def getVideos(post, path):
    try:
        url = requests.get(post['video_url'], stream=True) 
        vidName = generatePath(path, post['timestamp'], post['video_url'])
        writeFile(vidName, url)
    except KeyError:
        print(Fore.RED + 'Failed to download video from ' + post['post_url'])
            
def getAudio(post, path):
    audioName = post['audio_url'].rsplit('/', 1)[1]
    if '.mp3' in audioName:
        audioName = generatePath(path, post['timestamp'], post['audio_url'])
        finalUrl = requests.get(post['audio_url'], stream=True)
        writeFile(audioName, finalUrl)
    else:
        url = requests.get(post['audio_url'], allow_redirects=True)
        finalUrl = requests.get(url.url, stream=True)
        audioName = generatePath(path, post['timestamp'], finalUrl.url)
        if 'soundcloud' in post['audio_url']:
            audioName = audioName.split('?Policy')[0]
        writeFile(audioName, finalUrl)
    
def getMedia(blogName, mediaType):
    blogUrl = 'https://api.tumblr.com/v2/blog/' + blogName + '.tumblr.com/posts/' + mediaType + '?api_key=zEhk20rj71veq1vOkr7wZ5HoRSOuwRunDR7ErNhoMePhIiOlit'
    count = 0
    writePath = blogName
    while True:
        url = blogUrl + "&offset=" + str(count)        
        response = requests.get(url).json()
        
        if response['meta']['status'] == 200:
                        
            total_posts = response['response']['total_posts']
            if total_posts > 0:
                
                if not os.path.isdir(blogName):
                    os.mkdir(blogName)
                        
                if mediaType == 'audio':
                    writePath = blogName + '\Audio'
                elif mediaType == 'photo':
                    writePath = blogName + '\Pictures'
                elif mediaType == 'video':
                    writePath = blogName + '\Videos'
                                            
                if not os.path.isdir(writePath):
                    os.mkdir(writePath)
                    
            elif total_posts == 0:
                logging.warning('No ' + mediaType + ' posts were found at ' + blogName)
                print(Fore.LIGHTMAGENTA_EX + "\nIt seems this blog doesn't contain any " + mediaType + ' posts!')
                print("Try another option or try a different blog")
                break
            
            for post in response['response']['posts']:
                if mediaType == 'audio':
                    getAudio(post,writePath)
                elif mediaType == 'photo':
                    getPictures(post,writePath)
                elif mediaType == 'video':
                    getVideos(post,writePath)
                
            count += 20
            
            if count > total_posts:
                logging.info('All ' + mediaType + ' posts have been downloaded')
                print('\nDone!')
                break
            
        elif response['meta']['status'] == 404:
            print(Fore.RED + "\nWe couldn't find any blog with that name.")
            print(Fore.RED + "Check the spelling of the name or try a different blog")
            logging.warning('Blog not found: ' + blogName)
            break
        else:
            print(Fore.RED + "\nOops! We may have reached the rate limit. Try again in a couple of hours")
            logging.error('Server returned with status ' + str(response['meta']['status']))
            logging.error(str(response['meta']['msg']))
            break

def tumblrGetter():
    mediaTypes = {1:'photo', 2:'video',3:'audio' }
    while True:
        print('\nTumblr Media Getter')
        print('----------------------')
        print('Select an option:')
        print('1. Get Photos from a blog')
        print('2. Get Videos from a blog')
        print('3. Get Audio from a blog')
        print('0. Exit')
        data = input('Option: ')
        option = 1
        
        try:
            option = int(data)
            if option == 0:
                print(Fore.YELLOW + '\nGoodbye!')
                logging.info('Exiting application')
                time.sleep(1)
                break
            elif option > 0 and option < 4:
                blogName = input("Enter blog name: ")
                getMedia(blogName.lower(), mediaTypes[option])
            else:
                print(Fore.RED + "\nThat's not a valid option. Please try again")
        except ValueError:
            print(Fore.RED + "\nYou can only enter numbers. Please try again")

        print(Style.RESET_ALL)

def main():  
    logging.info('Starting application')
    while True:
        try:
            tumblrGetter()
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

