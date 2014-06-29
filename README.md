BackgroundNews
==============

speak articles in the webpage  
日々のニュースを定期的に音読します。 
このリポジトリはソフトウェアの配布が目的ではありません。  

googleニュース(https://news.google.co.jp)からRSS2.0によりニュースの記事を取得  
RSS2.0をパースして音声合成エンジンにより記事をwavファイルに変換し音読します。  
定期的にRSSを更新し、新しい記事が見つかると音読します。


install
=======
easy_install wxpython  
easy_install Feedparser  
apt-get install pyaudio  

音声合成には株式会社アクエストさんのAquesTalk2、AqKanji2Koeを使用しています  
 * http://www.a-quest.com/products/aquestalk.html  
 * http://www.a-quest.com/products/aqkanji2koe.html  

run
===

$python BackgroundNews.py

実行,コンパイル環境、ライブラリ
===============
- Ubuntu 13.10 64bit
- gcc (Ubuntu/Linaro 4.8.1-10ubuntu9) 4.8.1
- g++ (Ubuntu/Linaro 4.8.1-10ubuntu9) 4.8.1  
- python 2.7
- wxpython 2.8
- feedparser 5.1.3
- pyaudio 0.2.7-1

