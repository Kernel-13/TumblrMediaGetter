import requests
import os
import time
from colorama import Fore, Style, init
init(convert=True)
from pathlib import Path

def writeFile(finalPath, finalUrl):
    file = Path(finalPath)
    if not file.exists():
        with open(finalPath, 'wb') as f:
            f.write(finalUrl.content)
            print(Fore.GREEN + 'Downloaded ' + finalPath.rsplit('/', 1)[1])
    else:
        print(Fore.CYAN + 'File ' + finalPath.rsplit('/', 1)[1] + ' already exists')

def generatePath(path, timestamp, tumblrFileUrl):
    return path + '/' + str(timestamp) + '_' + tumblrFileUrl.rsplit('/', 1)[1]

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
        print(Fore.RED + 'Failed to download video from ' + post['video_url'])
            
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
                    writePath = blogName + '/Audio'
                elif mediaType == 'photo':
                    writePath = blogName + '/Pictures'
                elif mediaType == 'video':
                    writePath = blogName + '/Videos'
                                            
                if not os.path.isdir(writePath):
                    os.mkdir(writePath)
            
            for post in response['response']['posts']:
                if mediaType == 'audio':
                    getAudio(post,writePath)
                elif mediaType == 'photo':
                    getPictures(post,writePath)
                elif mediaType == 'video':
                    getVideos(post,writePath)
                
            count += 20
                
            if count > total_posts:
                print('\nDone!')
                break
        elif response['meta']['status'] == 404:
            print(Fore.RED + "\nWe couldn't find any blog with that name.")
            print(Fore.RED + "Check the spelling of the name or try a different blog")
            break
        else:
            print(Fore.RED + "\nOops! We may have reached the rate limit. Try again in a couple of hours")
            break

def tumblrGetter():
    mediaTypes = {1:'photo', 2:'video',3:'audio' }
    while True:
        print('\nTumblr Media Getter')
        print('----------------------')
        print('Select an option:')
        print('1. Download Photos from a blog')
        print('2. Download Videos from a blog')
        print('3. Download Audio from a blog')
        print('4. Exit')
        data = input('Option: ')
        option = 1
        
        try:
            option = int(data)
            if option == 4:
                print(Fore.YELLOW + '\nGoodbye!')
                time.sleep(2)
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
    while True:
        try:
            tumblrGetter()
            break
        except KeyboardInterrupt:
            print(Style.RESET_ALL)
            reply = input("You pressed Ctrl+Z. Do you want to exit the application? (Y/N): ")
            if reply.lower().startswith('y'):
                break
            
if __name__== "__main__":
    main()

