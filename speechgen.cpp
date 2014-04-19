
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>		// setlocale()
#include "AqKanji2Koe.h"
#include "AquesTalk2.h"
#include <fstream>
#include <string>
#include <iostream>

using namespace std;

string kanji2koe(string str, const string fname){
	int iret;
	int size = str.size();
	int nkoe = size * 5;
	char koe[nkoe];
	void *hAqKanji2Koe;

	hAqKanji2Koe = AqKanji2Koe_Create("./aq_dic", &iret);
	if(hAqKanji2Koe==0){
		fprintf(stderr, "ERR: can not initialize Dictionary(%d)\n", iret);
		fprintf(stderr, "USAGE: $ Kanji2KoeCmd (dic_dir) < in.txt > out.koe\n");
		char ch[sizeof(int)];
		sprintf(ch, "%d", iret);
		string sret(ch);
		return sret;
	}

	iret = AqKanji2Koe_Convert(hAqKanji2Koe, str.c_str(), koe, nkoe);
	if(iret!=0) {
		fprintf(stderr, "ERR: AqKanji2Koe_Convert()=%d\n", iret);
	}
	// 出力
	if(fname.length() > 0){
		ofstream ofs(fname.c_str());
		if(ofs){
			ofs << koe << endl;
		}
		cout << koe << endl;
	}

	AqKanji2Koe_Release(hAqKanji2Koe);
	return koe;
}

int sound_gen(string str, string wavf){
	/*
	 * str : sound string
	 * wavf : wave file name
	 */
	int 	size;
	int 	iret;

	// 音声合成
	unsigned char *wav = AquesTalk2_Synthe_Utf8(str.c_str(), 100, &size, NULL);
	if(wav==0){
		fprintf(stderr, "ERR:%d\n", size);
		return -1;
	}

	// 音声データ(wavフォーマット)の出力
	FILE *wavfile;
	wavfile = fopen(wavf.c_str(), "wb");
	if(wavfile == NULL){
		return -1;
	}
	fwrite(wav, 1, size, wavfile);
	fclose(wavfile);

	// 音声データバッファの開放
	AquesTalk2_FreeWave(wav);
 
	return 0;
}

void test(){
	string koef("koefile");
	string wavf("sound.wav");
	string koestring;
	koestring = kanji2koe("+16pt 「16進ダンプ」というのは、ファイルの中に書き込まれている数値を、16進数で書き下したものです。別に何進法で書き下してもいいのですが、こういう時は通例16進法を使います。", koef);
	if(koestring.length() < 2){
		return ;
	}
	sound_gen(koestring, wavf);
	return ;
}

int main(int argc, char **argv){
	/*
	 * usage:
	 *  soundgen string wave_filename [koe_filename]
	 */
	if(argc == 1){
		cout << "usage: soundgen string wave_filename [koe_filename]" << endl;
		return 1;
	}else if(argc < 3 || 4 < argc){
		cout << "usage: soundgen string wave_filename [koe_filename]" << endl;
		cout << "run test version" << endl;
		cout << "---------------" << endl;
		test();
		return 0;
	}

	string str(argv[1]);  // conversion source
	string wavf(argv[2]);  // output .wav filename
	string koef;  // output .txt speech text column filename

	if(argc > 3){
		koef = argv[3];
	}else{
		koef = "";
	}

	// convert article to speech text column
	string koe_str = kanji2koe(str, koef);
	if(koe_str.length() < 1){
		return 1;
	}

	// generate wave file
	int res = sound_gen(koe_str, wavf);

	return res;
}

