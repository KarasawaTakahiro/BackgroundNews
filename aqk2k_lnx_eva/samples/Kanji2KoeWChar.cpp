/*-------------------------------------------------------------
	Kanji2KoeWChar - かな漢字混じりテキストを音声記号列に変換

		音声合成用言語処理エンジン(AqKanji2Koe) 使用サンプル
		入出力文字列にwchar_tと
		メモリマップトファイルを用いた例

	$ Kanji2KoeWChar dic_dir < in.txt > out.koe

	■ビルド
	  あらかじめ 
	  libAqKanji2Koe.so.X.Xを ldconfigコマンドで共有ライブラリ登録しておくこと
	  $ g++  -I./lib -o Kanji2KoeWChar samples/Kanji2KoeWChar.cpp -lAqKanji2Koe

	■実行時の配置
		|- Kanji2KoeWChar
		|- aq_dic/		辞書フォルダ(aq_dic)を同じディレクトリに配置
			|- aqdic.bin 
			|- aq_user.dic (ユーザ辞書:任意)
			|- CREDITS

	■実行
	$ echo 音声合成テスト | ./Kanji2KoeWChar ./aq_dic
	コマンドラインオプションで辞書ファイルのディレクトリを指定する
  
	2011/01/14	N.Yamazaki	Creation
	2013/06/27	N.Yamazaki	Ver.2用に一部修正

-------------------------------------------------------------*/
#include <stdio.h>
#include <malloc.h>
#include <iostream>
#include <locale>
#include <AqKanji2Koe.h>
#include "aq_mmap.h"

void loadDic(const char *dir, void **ppSysDic, void **ppUserDic);

int main(int ac, char **av)
{
	int iret;

	// ロケールの設定(ファイルの入出力にwchar_tを使うために必要)
	setlocale(LC_ALL, "") ;

	// 辞書ファイルをメモリにマップ
	void *pSysDic;
	void *pUserDic;
	loadDic(av[1], &pSysDic, &pUserDic);
	if(pSysDic==0) return 1;	// load error

	// AqKanji2Koe初期化（インスタンス生成）
	void *hAqKanji2Koe = AqKanji2Koe_Create_Ptr(pSysDic, pUserDic, &iret);
	if(hAqKanji2Koe==0) return iret;

	for(;;){
		wchar_t wch[1024];
		if(fgetws(wch, 1024, stdin)==0) break;

		// 解析
		wchar_t wKoe[1024];
		iret =AqKanji2Koe_ConvertW(hAqKanji2Koe, wch, wKoe, 1024); //入出力はUTF16(LE)
		if(iret!=0) break;	// error

		std::wcout << wKoe << std::endl;
	}

	// AqKanji2Koe解放
	AqKanji2Koe_Release(hAqKanji2Koe);

	// 辞書データ解放
	// 	メモリマップトファイルのunmapは、CAqMmapのデストラクタで呼ばれる

	return iret;
}


CAqMmap<char> m_mmap_sysdic;
CAqMmap<char> m_mmap_userdic;

void loadDic(const char *dir, void **ppSysDic, void **ppUserDic)
{
	bool bret;
	std::string str;

	*ppSysDic=0;
	*ppUserDic=0;

	str = dir;
	if(str[str.size()-1]!='/') str += '/';
	str += "aqdic.bin";
	bret = m_mmap_sysdic.open(str.c_str());	// close()はmmapのデストラクタで呼ばれる
	if(bret==true) 	*ppSysDic = m_mmap_sysdic.begin();

	str = dir;
	if(str[str.size()-1]!='/') str += '/';
	str += "aq_user.dic";
	bret = m_mmap_userdic.open(str.c_str());
	if(bret==true) 	*ppUserDic = m_mmap_userdic.begin();
}
