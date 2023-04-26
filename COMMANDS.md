Commands are: </br>

​!addcom !points $(urlfetch http://surajbhari.info:5002/points?q=$(querystring)) </br>

​!addcom !callit $(urlfetch http://surajbhari.info:5002/callit?q=$(querystring)) -ul=moderator </br>

​!addcom !addpoints $(urlfetch http://surajbhari.info:5002/addpoints?q=$(querystring)) -ul=moderator </br>

​!addcom !removepoints $(urlfetch http://surajbhari.info:5002/removepoints?q=$(querystring)) -ul=moderator </br>

!addcom !lock $(urlfetch http://surajbhari.info:5002/lock) -ul=moderator </br>

!addcom !unlock $(urlfetch http://surajbhari.info:5002/unlock) -ul=moderator </br>

​!addcom !gamble $(urlfetch http://surajbhari.info:5002/gamble?q=$(query)) </br>

​!addcom !flip $(urlfetch http://surajbhari.info:5002/flip?q=$(querystring)) </br>

!addcom !give $(urlfetch http://surajbhari.info:5002/give?q=$(querystring)) </br>

!addcom !toppoints $(urlfetch http://surajbhari.info:5002/toppoints?q=$(querystring)) </br>