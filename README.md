# Search

主要是将用户的搜索字段，转移给Google，然后取回Google的搜索结果，并显示出来。
自己不擅长也不打算做UI，所以看起来会比较的丑，但是验证确实是能用的。欢迎大家的Pull Request。

Apache配置的时候，注意在配置文件（Debian /etc/apache2/apache2.conf）添加UTF的支持，否则中文乱码
且程序异常。
SetEnv PYTHONIOENCODING utf-8

TODO：
增加拣取谷歌快照的功能，这还是比较重要的。
