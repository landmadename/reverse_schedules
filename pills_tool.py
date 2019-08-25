import random
import pyperclip
colour = ["success", "info", "primary", "danger", "secondary"]
cl=[i[-1] for i in final_data]
cl=sorted(list(set(cl)),reverse=True)
h=['<button type="button" class="btn btn-'+random.choice(colour)+' pillers">'+i+'</button>' for i in cl]
h='\n'.join(h)
pyperclip.copy(h)