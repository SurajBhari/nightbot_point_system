Commands are: </br>

​!addcom !points $(urlfetch http://<your_ip>points?q=$(querystring)) </br>

​!addcom !callit $(urlfetch http://<your_ip>callit?q=$(querystring)) -ul=moderator </br>

​!addcom !addpoints $(urlfetch http://<your_ip>addpoints?q=$(querystring)) -ul=moderator </br>

​!addcom !removepoints $(urlfetch http://<your_ip>removepoints?q=$(querystring)) -ul=moderator </br>

!addcom !lock $(urlfetch http://<your_ip>lock) -ul=moderator </br>

!addcom !unlock $(urlfetch http://<your_ip>unlock) -ul=moderator </br>

​!addcom !gamble $(urlfetch http://<your_ip>gamble?q=$(query)) </br>

​!addcom !flip $(urlfetch http://<your_ip>flip?q=$(querystring)) </br>

!addcom !give $(urlfetch http://<your_ip>give?q=$(querystring)) </br>

!addcom !toppoints $(urlfetch http://<your_ip>top?q=$(querystring)) </br>
