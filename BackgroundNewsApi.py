#! /usr/bin/env python
# coding: utf-8

import datetime
import feedparser
import HTMLParser
import os.path
import pyaudio
import Queue
import sys
import time
import wave
from subprocess import Popen, PIPE
from threading import Thread

class StreamingException(BaseException): pass

def speechgen(string, wavfname, koefname=""):
    if not os.path.exists("speechgen"):
        raise IOError
    print "run speech gen", wavfname
    #print string
    popen = Popen(["./speechgen", string, wavfname, koefname], stdout=PIPE, stderr=PIPE)
    fincode = popen.wait()
    return fincode

class Article():
    title = u""
    link = u""
    category = u""
    pubDate = u""
    description = u""
    wav = u""

    def __init__(self, title=u"", link=u"", category=u"", pubDate=u"", description=u"", wav = u""):
        self.title = title
        self.link = link
        self.category = category
        self.pubDate = pubDate
        self.description = description
        self.wav = wav

class HtmlParser(HTMLParser.HTMLParser):
    string = ""

    def reflesh(self):
        self.string = ""

    def get_data(self):
        string = self.string
        self.string = ""
        return string

    def handle_data(self, data):
        self.string += data

class FeedParser():
    def __init__(self):
        pass

    def parse(self, url):
        """
        it returns the articles of feed obtained from the URL
        """
        hparser = HtmlParser()
        hparser.reflesh()
        feed = feedparser.parse(url)
        feeds = []
        for n in xrange(len(feed.entries)):
            article = Article()
            hparser.feed(feed.entries[n].title.replace("\n", ""))
            article.title = hparser.get_data()
            hparser.feed(feed.entries[n].link.replace("\n", ""))
            article.link = hparser.get_data()
            hparser.feed(feed.entries[n].category.replace("\n", ""))
            article.category = hparser.get_data()
            hparser.feed(feed.entries[n].published.replace("\n", ""))
            article.pubDate = hparser.get_data()
            hparser.feed(feed.entries[n].description.replace("\n", ""))
            article.description = hparser.get_data()
            feeds.append(article)
        return feeds

class Speech():
    UNKNOWN = -1
    WAIT = 0        # waiting for play
    PLAYING = 1     # is playing now
    FINISHED = 2    # complete playing
    STOPPED = 3      # play is interrupted

    _played = False     # true if it has played anything
    _playing = False    # true if it is playing now
    _finished = False   # true if it succeed to play
    _stopped = False    # true if playing is interrupted

    flag_stopped_que = False    # true when it be requested to stop playing

    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = None

    def getStreamState(self):
        statecode = []
        if not self._playing:
            statecode.append(self.WAIT)

        if self._playing:
          statecode.append(self.PLAYING)

        if self._finished:
          statecode.append(self.FINISHED)

        if self._stopped:
            statecode.append(self.STOPPED)

        return (self.UNKNOWN) if len(statecode) == 0 else tuple(statecode)


    def get_stream(self, wav, par_buffer=1024):
        """
        self.__wavf is define when streaming start.
        self.__wavf will be deleted when streaming finish.
        """
        self.__wavf = wavf = wave.open(wav, "rb")
        self.stream = self.pa.open(format = self.pa.get_format_from_width(wavf.getsampwidth()),
                channels = wavf.getnchannels(),
                rate = wavf.getframerate(),
                output = True
                )
        self.par_buffer = par_buffer
        #return self.stream

    def close_stream(self):
        """
        一時停止 == 停止
        streamは停止時に閉じても問題ない

        close stream
        """
        if not hasattr(self, "stream"):
            raise StreamingException()

        self.flag_stopped_que = True
        time.sleep(2 * float(self.par_buffer) / self.__wavf.getframerate())
        self.stream.stop_stream()
        self.stream.close()
        self.__wavf.close()
        self.th_stream.join()
        del self.stream
        self._playing = False
        self._finished = False
        self.flag_stopped_que = False

    def stop(self):
        """
        再生を（一時）停止する
        stop (pause) playing
        """
        if not hasattr(self, "stream"):
            raise StreamingException()

        self._stopped = True
        self.close_stream()

    def close(self):
        """
        close self
        """
        self.pa.terminate()

    def start_streaming(self):
        print "start_streaming is called"
        if hasattr(self, "stream"):
            self.th_stream = Thread(target=self.streaming)
            self.th_stream.daemon = True
            self.th_stream.start()
            self._playing = True

    def streaming(self):
        print "streaming is called"
        if not hasattr(self, "stream"):
            raise StreamingException()

        # flag
        self._finished = False
        self._stopped = False

        data = self.__wavf.readframes(self.par_buffer)
        while data != "":
            self.stream.write(data)
            data = self.__wavf.readframes(self.par_buffer)
            if self.flag_stopped_que:
                print "stopped que:", self.flag_stopped_que
                self.flag_stopped_que = False
                break
        else:
            self._finished = True

    def stream_is_active(self):
        if not hasattr(self, "stream"):
            return False
        elif self.stream == None:
            return False
        else:
            return self.stream.is_active()


class ArticleLibraly():
    """
    Database API
    """
    def __init__(self):
        """
        int     id
        string  title
        int     playedNum
        string  wavPath
        string  date
        """
        pass

class BackgroundNewsApi(Speech):
    """
    UNKNOWN = -1
    WAIT = 0        # waiting for play
    PLAYING = 1     # is playing now
    FINISHED = 2    # complete playing
    STOPPED = 3     # play is interrupted
    """

    def __init__(self):
        Speech.__init__(self)
        self._playq = Queue.Queue()  # to play (Article, .wav path)
        self._translateq = Queue.Queue()  # to .wav

        self.articles = None
        self.playing = None
        self.num_playq = 0
        self.num_translateq = 0

    def parse(self, url):
        """
        str url
        """
        return FeedParser().parse(url)

    def storage(self, article):
        """
        regist article into DB
        """
        pass

    def pushPlayQueue(self, article):
        """
        Article article
        """
        self._playq.put(article)
        self.num_playq += 1

    def getPlayQueue(self):
        """
        raise Queue.Empry error when self._playq is empty.
        """
        ret = self._playq.get_nowait()
        self.num_playq -= 1
        print "getPlayQueue:", ret
        return ret

    def getPlayQueueNum(self):
        return self.num_playq

    def pushTranslateQueue(self, article):
        """
        Article article
        """
        self._translateq.put(article)
        self.num_translateq += 1

    def getTranslateQueue(self):
        """
        raise Queue.Empry error when self._translateq is empty.
        """
        res = self._translateq.get_nowait()
        self.num_translateq += 1
        return res

    def getTranslateQueueNum(self):
        return self.num_translateq

    def translate(self, string, fname):
        """
        return code(success:0)
        """
        return speechgen(string, fname)

    def playNext(self, callNextWav=None):
        """
        raise Queue.Empry error when self._playq is empty.
        return playing article
        """
        # check the status of the stream
        if callNextWav != None:
            if not os.path.exists(callNextWav):
                raise IOError
            self.play(callNextWav)
            while self.getStreamState():
                time.sleep(0.1)
        # speak next article
        article = self.getPlayQueue()
        ret = self.play(article.wav)
        if ret:
            print "playNext return:", article
            return article
        else:
            print "playNext return:", None
            return None

    def play(self, wav):
        """
        raise IOError when it not found wavfile.
        """
        if not os.path.exists(wav):
            raise IOError, path
        self.get_stream(wav)
        self.start_streaming()
        print "play complete"
        return self.stream_is_active()

if __name__ == "__main__":
    """
    url = sys.argv[1]
    fp = FeedParser()
    articles = fp.parse(url)
    speech = Speech()
    wavdir = "articles"
    wavfs = []

    for item in articles:
        while True:
            wavfn = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".wav"
            wavfn = os.path.join(wavdir, wavfn)
            if os.path.exists(wavfn):
                time.sleep(0.1)
            else:
                break
        print "generating %s" % wavfn
        res = speechgen(item.description, wavfn)
        if res == 0:
            wavfs.append(os.path.abspath(wavfn))
            print "complete!"
        else:
            print "failed..."

    for wavf in wavfs:
        speech.get_stream(wavf)
        speech.play()
        while speech.stream_is_active():
            time.sleep(0.1)
        time.sleep(3)

    speech.close()
    """
    api = BackgroundNewsApi()

    def allTranslate():
        while True:
            time.sleep(0.1)
            try:
                item = api.getTranslateQueue()
            except Queue.Empty:
                print "translate queue is empty"
                time.sleep(10)
                continue
            print "translate:", item.title
            while True:
                path = "articles/"+datetime.datetime.now().strftime("%Y%m%d%H%M%S") + ".wav"
                if not os.path.exists(path):
                    break
            code = api.translate(item.description, path)
            if code == 0:
                item.wav = os.path.abspath(path)
                print "translate complete:", item.wav
                api.pushPlayQueue(item)
            else:
                print "translate failed:", item.title

    def autoplay():
        while True:
            try:
                article = api.playNext()
                print "streaming start--------: %s" % article.wav
            except Queue.Empty:
                print "play queue is empty"
                time.sleep(10)
                continue
            except IOError, e:
                print "wav file is not found"
                print e
            except StreamingException:
                print "streaming now ..."
                time.sleep(10)
                continue


    th_translate = Thread(target=allTranslate)
    th_translate.daemon = True
    th_translate.start()
    th_autoplay = Thread(target=autoplay)
    th_autoplay.daemon = True
    th_autoplay.start()

    while True:
        api.parse("https://news.google.com/news/feeds?ned=us&ie=UTF-8&oe=UTF-8&q&output=rss&num=30&hl=ja")
        print "%d articles was loaded" % len(api.articles)

        for item in api.articles:
            api.pushTranslateQueue(item)

        api.articles = []

        time.sleep(300)




