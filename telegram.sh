if curl --silent --fail -m 5 -o /dev/null -G  -x socks5://v3_418198005:kcIrdLgF@s5.priv.opennetwork.cc:1080 https://api.telegram.org/bot553491516:AAGdnVspu211pvddLJi2zCrFj4bDQHDc2gM/getMe; then
    echo online;
else
    echo offline;
fi