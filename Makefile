speechgen : speechgen.cpp
	g++ speechgen.cpp -o speechgen -I. -lAqKanji2Koe -lAquesTalk2Eva

mecab_test : mecab_test.cpp
	g++ mecab_test.cpp -o mecab_test -lmecab
