#!/bin/sh -x

date=`date '+%Y-%m-%d-%H:%M'`
cachedir=/home/ubuntu/radio/cache/
mp3dir=/home/ubuntu/radio/mp3/
playerurl=http://radiko.jp/apps/js/flash/myplayer-release.swf
playerfile=$cachedir/player.swf
keyfile=./authkey.png
tmpfile="./${1}_${date}"
mp3file="${mp3dir}${1}_${date}.mp3"

if [ $# -ge 2 ]; then
  station=$1
  DURATION=`expr $2 \* 60`
  if [ $# -eq 3 ]; then
    delaysec=$3
  else
    delaysec=0
  fi
else
  echo "usage : $0 station_name duration(minuites) [offset(sec)]"
  exit 1
fi

cd $cachedir

#
# get player
#
if [ ! -f $playerfile ]; then
  /usr/bin/wget -q -O $playerfile $playerurl

  if [ $? -ne 0 ]; then
    echo "failed get player"
    exit 1
  fi
fi

#
# get keydata (need swftool)
#
if [ ! -f $keyfile ]; then
  swfextract -b 12 $playerfile -o $keyfile

  if [ ! -f $keyfile ]; then
    echo "failed get keydata"
    exit 1
  fi
fi

if [ -f auth1_fms ]; then
  rm -f auth1_fms
fi

#
# access auth1_fms
#
/usr/bin/wget -q \
     --header="pragma: no-cache" \
     --header="X-Radiko-App: pc_ts" \
     --header="X-Radiko-App-Version: 4.0.0" \
     --header="X-Radiko-User: test-stream" \
     --header="X-Radiko-Device: pc" \
     --post-data='\r\n' \
     --no-check-certificate \
     --save-headers \
     https://radiko.jp/v2/api/auth1_fms

if [ $? -ne 0 ]; then
  echo "failed auth1 process"
  exit 1
fi

#
# get partial key
#
authtoken=`perl -ne 'print $1 if(/x-radiko-authtoken: ([\w-]+)/i)' auth1_fms`
offset=`perl -ne 'print $1 if(/x-radiko-keyoffset: (\d+)/i)' auth1_fms`
length=`perl -ne 'print $1 if(/x-radiko-keylength: (\d+)/i)' auth1_fms`

partialkey=`dd if=$keyfile bs=1 skip=${offset} count=${length} 2> /dev/null | base64`
echo "authtoken: ${authtoken} \noffset: ${offset} length: ${length} \npartialkey: 

$partialkey"

rm -f auth1_fms

if [ -f auth2_fms ]; then
  rm -f auth2_fms
fi

#
# access auth2_fms
#
/usr/bin/wget -q \
     --header="pragma: no-cache" \
     --header="X-Radiko-App: pc_ts" \
     --header="X-Radiko-App-Version: 4.0.0" \
     --header="X-Radiko-User: test-stream" \
     --header="X-Radiko-Device: pc" \
     --header="X-Radiko-AuthToken: ${authtoken}" \
     --header="X-Radiko-PartialKey: ${partialkey}" \
     --post-data='\r\n' \
     --no-check-certificate \
     https://radiko.jp/v2/api/auth2_fms

if [ $? -ne 0 -o ! -f auth2_fms ]; then
  echo "failed auth2 process"
  exit 1
fi

echo "authentication success"
areaid=`perl -ne 'print $1 if(/^([^,]+),/i)' auth2_fms`
echo "areaid: $areaid"

rm -f auth2_fms

# offset time
echo "Sleep ${delaysec} sec."
sleep $delaysec

#
# rtmpdump
#
/usr/bin/rtmpdump -v \
         -r "rtmpe://f-radiko.smartstream.ne.jp" \
         --playpath "simul-stream.stream" \
         --app "${station}/_definst_" \
         -W $playerurl \
         -C S:"" -C S:"" -C S:"" -C S:$authtoken \
         --live \
         --stop $DURATION \
         -o $tmpfile

/usr/bin/ffmpeg -y -i $tmpfile -acodec libmp3lame -ab 64k $mp3file
rm -f $tmpfile

exit
