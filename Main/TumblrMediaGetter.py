import requests
import os
import time
import colorama
from colorama import Fore, Style, init
init(convert=True)
from pathlib import Path

def writeMediaFile(fileName, finalUrl):
    file = Path(fileName)
    if not file.exists():
        with open(fileName, 'wb') as f:
            f.write(finalUrl.content)
            print(Fore.GREEN + 'Saving ' + os.getcwd() + '/' + fileName + ' -- Success!')
    else:
        print(Fore.CYAN + 'File ' + fileName + ' already exists')

def getPictures(post, path):  
    for photo in post['photos']:
        url = requests.get(photo['original_size']['url'], stream=True) 
        picName = path + '/' + photo['original_size']['url'].rsplit('/', 1)[1]
        writeMediaFile(picName, url)   
     
def getVideos(post, path):
    try:
        url = requests.get(post['video_url'], stream=True) 
        vidName = path + '/' + post['video_url'].rsplit('/', 1)[1]
        writeMediaFile(vidName, url)
    except KeyError:
        print(Fore.RED + 'Failed to download video from ' + post['video_url'])
            
def getAudios(post, path):
    audioName = post['audio_url'].rsplit('/', 1)[1]
    if '.mp3' in audioName:
        audioName = path + '/' + audioName
        finalUrl = requests.get(post['audio_url'], stream=True)
        writeMediaFile(audioName, finalUrl)
        
    else:
        url = requests.get(post['audio_url'], allow_redirects=True)
        finalUrl = requests.get(url.url, stream=True)
        audioName = path + '/' + finalUrl.url.rsplit('/', 1)[1]
        if 'soundcloud' in post['audio_url']:
            audioName, rest = audioName.split('?Policy')
        writeMediaFile(audioName, finalUrl)
    
def getMedia(blogName, mediaType):
    blogUrl = 'https://api.tumblr.com/v2/blog/' + blogName + '.tumblr.com/posts/' + mediaType + '?api_key=zEhk20rj71veq1vOkr7wZ5HoRSOuwRunDR7ErNhoMePhIiOlit'
    count = 0
    writePath = blogName
    posts_still_left = True
    while posts_still_left:
        
        request_url = blogUrl + "&offset=" + str(count)        
        tumblr_response = requests.get(request_url).json()
        total_posts = tumblr_response['response']['total_posts']
        
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
        
        for post in tumblr_response['response']['posts']:
            if mediaType == 'audio':
                getAudios(post,writePath)
            elif mediaType == 'photo':
                getPictures(post,writePath)
            elif mediaType == 'video':
                getVideos(post,writePath)
                
        count += 20
        
        if count > total_posts:
            posts_still_left = False
    
    print('\nDone!')

def tumblrGetter():
    mediaTypes = {1:'photo', 2:'video',3:'audio' }
    exit=False
    while not exit:
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
        except ValueError:
            option = 5

        if option == 4:
            print(Fore.YELLOW + '\nGoodbye!')
            exit = True
            time.sleep(2)
        elif option > 0 and option < 4:
            print('')
            blogName = input("Enter blog's name: ")
            getMedia(blogName, mediaTypes[option])
        else:
            print(Fore.RED + "\nThat's not a valid option. Please try again\n")

        print(Style.RESET_ALL)
    
    
  
def main():
    exit = False
    while exit is False:
        try:
            tumblrGetter()
            exit = True
        except KeyboardInterrupt:
            print(Style.RESET_ALL)
            reply = input("You pressed Ctrl+Z. Do you want to exit the application? (Y/N): ")
            if reply.lower().startswith('y'):
                exit = True
            
    
if __name__== "__main__":
    main()

