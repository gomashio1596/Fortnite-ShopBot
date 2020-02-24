# Fortnite-ShopBot

Fortniteのショップ画像ジェネレーター

サンプル
![itemshop](https://user-images.githubusercontent.com/53356872/75128885-b9b21780-5709-11ea-9e2b-41e23af60981.png)

# 導入
[Python 3.5](https://www.python.org/downloads "Pythonダウンロード")以上が必要  
INSTALL.batを実行する  
configに情報を書き込む  
RUN.batを実行する

# config

```
banner         : アイテムの種類のバナーのテキスト
backpack       : アイテムの種類のバッグアクセサリーのテキスト
outfit         : アイテムの種類のコスチュームのテキスト
contrail       : アイテムの種類のコントレイルのテキスト
emote          : アイテムの種類のエモートのテキスト
emoji          : アイテムの種類のエモートアイコンのテキスト
glider         : アイテムの種類のグライダーのテキスト
wrap           : アイテムの種類のラップのテキスト
loadingscreen  : アイテムの種類のロード画面のテキスト
music          : アイテムの種類の音楽のテキスト
pet            : アイテムの種類のペットのテキスト
pickaxe        : アイテムの種類の収集ツールのテキスト
spray          : アイテムの種類のスプレーのテキスト
toy            : アイテムの種類のおもちゃのテキスト
featured       : ショップのフィーチャーのテキスト
daily          : ショップのデイリーのテキスト
date           : 時刻の形式 後述
hour           : UTC(世界標準時)からの時間のずれ
language       : ショップの言語
enabled        : 特別オファーのテキストを自動で置き換えるかの設定
email          : Epic Gamesアカウントのメールアドレス 後述
password       : Epic Gamesアカウントのパスワード
user-agent     : ユーザー情報
launcher_token : ランチャーのトークン
fortnite_token : Fortniteのトークン
monitor-change : 自動でショップの変更を検知するか
namefont       : アイテムの名前の表示に使うフォント
categoryfont   : アイテムの種類の表示に使うフォント
api-key        : Fortnite-API.comのAPIキー 後述
```

# なんでアカウントの情報がいるの?
特別オファーのテキストを取得するにはアカウントにログインし  
アクセストークンを取得する必要がある

# exchange_codeの入力を求められた
exchange_codeを[公式サイト](https://www.epicgames.com "epicgames.com")でボットのアカウントにログインし、
[ログイン](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fexchange "ログイン")で取得してください

# 時刻形式
%Y で年  
%B で月  
%#d又は%-d で日  
%A で曜日  
%H で時  
%M で分  
%S で秒

# 言語
en / ar / de / es-419 / es / fr / it / ja / ko / pl / pt-BR / ru / tr / zh-CN / zh-Hant

# APIキー  
```
Discordアカウントが必要
```
[ここ](https://discordapp.com/invite/AqzEcMm "Fortnite-API.com 招待リンク")からサーバーに参加  
[このサイト](https://fortnite-api.com/profile "Fortnite-API.com")からAPIキーを生成、コピーしてconfigのapi-keyに張り付ける

# フォント
Fortniteで使用しているフォント  
日本語  
アイテム名: [JTCじゃんけんU](https://font.designers-garage.jp/products/detail/2338 "NISフォント")  
アイテムの種類: [Noto Sans JP](https://fonts.google.com/specimen/Noto+Sans+JP "Google Fonts")  
英語  
アイテム名: [Burbank](https://houseind.com/hi/burbank "House Industries")  
アイテムの種類: [Noto Sans](https://fonts.google.com/specimen/Noto+Sans "Google Fonts")  

無料で似ているフォント  
日本語  
アイテム名: [GN-キルゴU](http://getsuren.com/killgoU.html "GN's Side")  
英語  
アイテム名: [Luckiest Guy](https://fonts.google.com/specimen/Luckiest+Guy "Google Fonts")  

フォントは assets/fonts の中に入れてください
