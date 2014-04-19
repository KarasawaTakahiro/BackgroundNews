#include <iostream>
#include <mecab.h>
#include <vector>
#include <string>

#define CHECK(eval) if (! eval) { \
   const char *e = tagger ? tagger->what() : MeCab::getTaggerError(); \
   std::cerr << "Exception:" << e << std::endl; \
   delete tagger; \
   return -1; }

using namespace std;

vector<string> split(const string &str, char delim);
vector<string> get_reading(const char *input);

	void test(){
  string input("「16進ダンプ」というのは、ファイルの中に書き込まれている数値を、16進数で書き下したものです。別に何進法で書き下してもいいのですが、こういう時は通例16進法を使います。");
  vector<string> yomi = get_reading(input.c_str());
  vector<string>::iterator itr;

  if (argc > 1){
	  input = argv[1];
  }

  itr = yomi.begin();
  while(itr != yomi.end()){
	  cout << *itr << endl;
	  itr++;
  }
}

vector<string> get_reading(const char *input){
  vector<string> res;

  MeCab::Tagger *tagger = MeCab::createTagger("");
  //CHECK(tagger);
  const MeCab::Node* node = tagger->parseToNode(input);
  //CHECK(node);

  vector<string> ana;
  for (; node; node = node->next) {
	  if (node->stat == MECAB_BOS_NODE){
		  continue;
	  }else if (node->stat == MECAB_EOS_NODE) {
			break;
		}
		ana = split(node->feature, ',');

		res.push_back(ana[7]);
  }

  delete tagger;

  return res;
}

vector<string> split(const string &str, char delim){
	vector<string> res;
	size_t current = 0, found;
	while((found = str.find_first_of(delim, current)) != string::npos){
		res.push_back(string(str, current, found - current));
		current = found + 1;
	}
	res.push_back(string(str, current, str.size() - current));
	return res;
}

int main (int argc, char **argv) {
	test();
	return 0;
}

