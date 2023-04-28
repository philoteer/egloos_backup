# egloos_backup

이글루스가 문닫는다기에 만들고 있습니다.

As/is; at your own RISC

실행법: 
```
python3 egloos_dl.py

User ID? 다운받고자 하는 이글루스 계정 ID
Delay per download? [default: 100] 파일을 하나 다운로드할 때 마다 대기할 시간. 짧을 수록 빠르나 이글루스쪽에서 싫어할 수 있음 (단위: ms; 기본값: 100)
Reverse the post order? [Y/N; default: N] Y = 포스트의 순서를 뒤집음. N = 그대로 둠 (기본값)
Download all posts? [\"ALL\" for all posts; \"CAT\" for one category. default:ALL] ALL = 모든 포스트를 다운받음. CAT = 카테고리 하나만 다운받음
```

윈도우 바이너리 다운로드: https://github.com/philoteer/egloos_backup/releases/tag/rel1 

(*윈도 바이너리는 버그패치를 덜 했으므로 그냥 파이썬 스크립트 받아서 돌리시는 편이 나을 수 있습네다.)
