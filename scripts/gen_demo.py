# генерация демо-данных «Первый глоток»
import json, csv, random, datetime as dt
from pathlib import Path
random.seed(2026)
OUT = Path("data/demo"); OUT.mkdir(parents=True, exist_ok=True)
M = [("Эспрессо","Кофе",150,0.7,""),("Американо","Кофе",200,1.0,""),("Капучино","Кофе",300,1.5,"молоко"),
("Латте","Кофе",320,1.5,"молоко"),("Флэт уайт","Кофе",330,1.5,"молоко"),("Раф","Кофе",380,2.0,"молоко"),
("Мокка","Кофе",350,1.7,"молоко"),("Айс-латте","Кофе",340,1.5,"молоко"),("Айс-американо","Кофе",260,1.0,""),
("Фильтр-кофе","Кофе",180,0.5,""),("Чай чёрный","Не кофе",180,0.7,""),("Чай зелёный","Не кофе",180,0.7,""),
("Чай облепиховый","Не кофе",260,1.0,""),("Какао","Не кофе",300,1.5,"молоко"),("Горячий шоколад","Не кофе",330,1.5,"молоко"),
("Морс ягодный","Не кофе",200,0.3,""),("Круассан классический","Выпечка и еда",160,0.3,"глютен, молоко, яйца"),
("Круассан с миндалём","Выпечка и еда",210,0.3,"глютен, молоко, яйца, орехи"),("Сырник","Выпечка и еда",220,0.5,"глютен, молоко, яйца"),
("Сэндвич с индейкой","Выпечка и еда",330,0.7,"глютен, молоко"),("Овсяная каша с ягодами","Выпечка и еда",250,0.6,"глютен"),
("Гранола с йогуртом","Выпечка и еда",240,0.3,"глютен, молоко, орехи"),("Маффин шоколадный","Выпечка и еда",170,0.3,"глютен, молоко, яйца"),
("Печенье овсяное","Выпечка и еда",90,0.1,"глютен, яйца")]
SIZES = {2,3,4,5,6,7,8,9,10,14,15}
menu=[]
for i,(n,c,p,l,a) in enumerate(M,1):
    drink = c!="Выпечка и еда"
    menu.append({"id":i,"name":n,"category":c,"price_m":p,"load":l,"allergens":[x for x in a.split(", ") if x],
                 "sizes":["S","M","L"] if i in SIZES else ["M"],
                 "milk": drink and "молоко" in a, "syrup": i<=10 or i in (14,15), "extra_shot": i<=8,
                 "in_stop_list": False})
mods = {"size":{"S":-40,"M":0,"L":50},
        "milk":{"коровье":0,"безлактозное":0,"овсяное":60,"миндальное":60},
        "syrup":40,"extra_shot":{"price":70,"load":0.3}}
settings = {"window_start":"07:45","window_end":"10:30","step_min":5,"slot_capacity":8.0,
            "preorder_share":0.60,"min_lead_min":10,"order_from":"06:30","cancel_before_min":5,
            "ready_keep_min":15,"max_units":5,"timezone":"Europe/Moscow","demo_time":None}
users = {"guests":[{"tg_id":900000001,"name":"Павел"},{"tg_id":900000002,"name":"Алина"},{"tg_id":900000003,"name":"Ольга"}],
         "staff":[{"login":"barista","role":"barista","name":"Денис (бариста)","password_env":"BARISTA_PASSWORD"},
                  {"login":"manager","role":"manager","name":"Марина (управляющая)","password_env":"MANAGER_PASSWORD"}]}
def line(item, size="M", milk="коровье", syrup=False, shot=0, qty=1):
    it = menu[item-1]
    price = it["price_m"]+mods["size"][size]+mods["milk"][milk]+(40 if syrup else 0)+70*shot
    load = round(it["load"]+0.3*shot,2)
    return {"item_id":item,"name":it["name"],"size":size,"milk":milk if it["milk"] else None,
            "syrup":syrup,"extra_shot":shot,"qty":qty,"unit_price":price,"unit_load":load}
def rand_line():
    i = random.choice(range(1,25)); it = menu[i-1]
    size = random.choice(it["sizes"]); milk = random.choice(list(mods["milk"])) if it["milk"] else "коровье"
    syrup = it["syrup"] and random.random()<0.2; shot = 1 if it["extra_shot"] and random.random()<0.15 else 0
    return line(i,size,milk,syrup,shot,1)
def totals(lines):
    return sum(l["unit_price"]*l["qty"] for l in lines), round(sum(l["unit_load"]*l["qty"] for l in lines),2)
def rand_order(maxload=4.8):
    while True:
        lines=[rand_line() for _ in range(random.choice([1,1,2,2,3]))]
        p,l=totals(lines)
        if l<=maxload: return lines,p,l
SLOTS=[(dt.datetime(2000,1,1,7,45)+dt.timedelta(minutes=5*k)).strftime("%H:%M") for k in range(34)]
assert len(SLOTS)==34 and SLOTS[-1]=="10:30"
# история: 5 будних дней × 12 заказов = 60
days=[dt.date(2026,10,26)+dt.timedelta(d) for d in range(5)]
statuses = ["Выдан"]*47+["Отменён гостем"]*6+["Отменён баром"]*3+["Просрочен"]*4
random.shuffle(statuses)
hist=[]; k=0
for d in days:
    used={}
    for n in range(1,13):
        while True:
            slot=random.choice(SLOTS[6:24]); lines,p,l=rand_order()
            if used.get(slot,0)+l<=4.8: used[slot]=used.get(slot,0)+l; break
        st=statuses[k]; k+=1
        guest=random.choice(users["guests"])
        s=dt.datetime.combine(d,dt.time.fromisoformat(slot))
        created=s-dt.timedelta(minutes=random.randint(15,70))
        rec={"order_no":f"{n:03d}","date":d.isoformat(),"slot":slot,"guest_tg_id":guest["tg_id"],"guest_name":guest["name"],
             "status":st,"total_rub":p,"load":l,"items":json.dumps(lines,ensure_ascii=False),
             "created_at":created.isoformat(timespec="seconds"),"accepted_at":created.isoformat(timespec="seconds"),
             "ready_at":"","issued_at":"","cancel_reason":""}
        if st in ("Выдан","Просрочен"):
            ready=s-dt.timedelta(minutes=random.randint(0,3)); rec["ready_at"]=ready.isoformat(timespec="seconds")
            if st=="Выдан": rec["issued_at"]=(ready+dt.timedelta(minutes=random.randint(1,9))).isoformat(timespec="seconds")
        if st=="Отменён баром": rec["cancel_reason"]="Позиция в стоп-листе"
        hist.append(rec)
# пиковый набор PG-4: 40 заказов, слоты 08:30–09:25, лимит 4,8 не превышен
peak=[]; load={s:0.0 for s in SLOTS[9:21]}
n=0
while n<40:
    lines,p,l=rand_order(2.4)
    free=[s for s in load if load[s]+l<=4.8]
    if not free: continue
    s=min(free,key=lambda x:load[x]); load[s]=round(load[s]+l,2); n+=1
    peak.append({"order_no":f"{n:03d}","slot":s,"guest_tg_id":users["guests"][n%3]["tg_id"],"status":"Принят",
                 "total_rub":p,"load":l,"items":lines})
tests={
 "T1":{"lines":[line(3,"M","овсяное"),line(17)],"expect_price":520,"expect_load":1.8},
 "T2":{"slot":"08:35","slot_load":3.0,"new_load":1.8,"expect":"доступен; +круассан 5,1 > 4,8 — недоступен"},
 "T3":{"lines":[line(6,"L","овсяное",qty=2)],"expect_price":980,"expect_load":4.0},
 "T4":{"lines":[line(4,qty=4)],"expect_load":6.0,"expect":"недоступно ни в одном слоте"},
 "T5":{"slot":"09:00","cancel_ok":"08:55:00","cancel_fail":"08:55:01"},
 "T6":{"ready_at":"08:58","expect_overdue_at":"09:13"},
 "T7":{"role":"barista","forbidden":["/manager/menu","/manager/summary"]},
 "T8":{"stop_item":"Круассан классический","expect_sec":10},
 "T9":{"demo_time":"08:20","expect_first_slot":"08:30"}}
for name,obj in [("menu.json",menu),("modifiers.json",mods),("settings.json",settings),("users.json",users),
                 ("orders_peak40.json",peak),("testcases.json",tests)]:
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
with open(OUT/"orders_history.csv","w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=list(hist[0]),delimiter=";"); w.writeheader(); w.writerows(hist)
# проверка
assert len(menu)==24 and len({m["category"] for m in menu})==3
assert totals(tests["T1"]["lines"])==(520,1.8) and totals(tests["T3"]["lines"])==(980,4.0) and totals(tests["T4"]["lines"])[1]==6.0
assert len(hist)==60 and len(peak)==40 and max(load.values())<=4.8
from collections import Counter
print("menu 24 ok; T1/T3/T4 ok; history",Counter(h["status"] for h in hist)); print("peak max slot load",max(load.values()), "slots", len(load))
