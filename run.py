from Player import Player
from curses import ALL_MOUSE_EVENTS
import discord
import random
import time

with open('./.env', 'r') as f:
    key = f.read()

TOKEN = str(key)

Intents = discord.Intents.default()
Intents.members = True
client = discord.Client(intents=Intents)

players = []
all_members = []
game_members = []

jobs = ['Werewolf', 'Seer', 'Villager', 'Knight', 'Madman','Bakery']
job_setting = {'Werewolf': 0, 'Seer': 0, 'Villager': 0, 'Knight': 0, 'Madman':0, 'Bakery':0}
job_name = {'Werewolf': '人狼', 'Seer': '占い師', 'Villager': '村人', 'Knight': '狩人', 'Madman':'狂人', 'Bakery':'パン屋'}
job_priority = {'Werewolf': 0, 'Seer': 1, 'Villager': 2, 'Knight': 3, 'Madman':4, 'Bakery':5}

act_stack = []
target_count = 0
bakery_flag = False #パン屋の生死判定を決定する変数


@client.event
async def on_ready():
    print('Start GM Bot')


@client.event
async def on_message(message):
    args = message.content.split(' ')
    global phase
    if message.author.bot:
        return
    if args[0] == 'getm':
        text = 'メンバーリスト'
        for mem in message.guild.members:
            # print(mem.id)
            text += '\n - ' + str(mem)
            if not(str(mem.name) in all_members):
                all_members.append((mem.id, mem.name))

        await message.channel.send(text)

    if args[0] == 'setp':
        text = '参加者リスト'
        for arg in args:
            print(arg)
            for key, value in all_members:
                if value == str(arg):
                    p = (key, value)
                    game_members.append(p)
                    text += '\n - ' + str(arg)

        await message.channel.send(text)

    if args[0] == 'setj':
        text = '役職'
        for arg in args:
            tmp = arg.split(':')
            print(tmp)
            if tmp[0] in jobs:
                job_setting[tmp[0]] = int(tmp[1])
                text += '\n - ' + job_name[tmp[0]] + ' : ' + tmp[1] + '人'
        await message.channel.send(text)

    if args[0] == 'gamestart':
        js = []
        text = '夜になりました。役職を確認してください。'
        for key in job_setting:
            for i in range(job_setting[key]):
                js.append(key)
        print(js)
        random.shuffle(js)
        print(js)
        print(game_members)

        villager_ids = []

        for i in range(len(game_members)):
            p = Player(game_members[i][0], game_members[i][1], js[i])
            players.append(p)
            if not (p.get_is_wolf()) and p.get_job_name() != 'Seer':
                villager_ids.append(i)

        print(villager_ids)
        random.shuffle(villager_ids)
        for p in players:
            if p.get_job_name() == 'Seer':
                text += '\n 占い師に送るやつ'+p.act(players[villager_ids[0]])
                print(text)
                # TODO: 本番ではコメントアウト外す
                # await client.get_user(p.get_id()).send(text)

        # debug
        text += '\n debug'
        for p in players:
            text += '\n - ' + p.get_name() + ': ' + p.get_job()

        await message.channel.send(text)

    if args[0] == 'getjob':
        text = 'あなたの役職は　'
        for p in players:
            if message.author.id == p.get_id():
                text += p.get_job() + '　です。'
        await message.author.send(text)

    if args[0] == 'vote':
        text = ''
        for p in players:
            if p.get_id() == message.author.id:
                for p2 in players:
                    if args[1] == p2.get_name() and not(p.is_voted()):
                        p.vote(p2)
                        text += p.get_name() + ' さんは ' + p2.get_name() + '　さんに投票しました。'

        await message.channel.send(text)

    if args[0] == 'votend':
        text = '投票結果'
        vote_list = {}
        for p in players:
            if p.get_voted_target() != '':
                vote_list[p.get_voted_target()] = 0
        for p in players:
            if p.get_voted_target() != '':
                vote_list[p.get_voted_target()] += 1
        for v in vote_list.keys():
            text += '\n - ' + v + ' : ' + str(vote_list[v]) + '票'
        await message.channel.send(text)
        time.sleep(1)
        max = -1
        for v in vote_list.keys():
            if max < vote_list[v]:
                max = vote_list[v]
                text = v
        for p in players:
            if p.get_name() == text:
                p.set_dead(True)
        text += ' さんが投票により処刑されます。'
        await message.channel.send(text)
        time.sleep(2)
        await message.channel.send('夜になりました。夜のアクションをしてください。')

    if args[0] == 'act':
        text = 'あなたの役職は '
        for p in players:
            if message.author.id == p.get_id():
                text += p.get_job() + ' です。\n' + p.message()
        await message.author.send(text)

    if args[0] == 'target':
        global target_count
        text = '指定したターゲットにアクションをおこします。'
        for p in players:
            if message.author.id == p.get_id():
                for p2 in players:
                    if args[1] == p2.get_name() and not(p.is_acted()):
                        target_count += 1
                        act_stack.append((p, p2))
                        p.set_acted(True)
        await message.author.send(text)

# 全プレイヤーの行動が終了
        if target_count >= len(players):
            target_count = 0
            text = ''
            attacked_player = act_stack[0][0]
            for i in range(len(act_stack)):
                for j in range(len(act_stack)):
                    if job_priority[act_stack[i][0].get_job_name()] > job_priority[act_stack[j][0].get_job_name()]:
                        tmp = act_stack[i]
                        act_stack[i] = act_stack[j]
                        act_stack[j] = tmp
            for act in act_stack:
                text += act[0].act(act[1])
                print(act[0].get_name() + 'が' +
                      act[1].get_name() + 'にアクションしました')
                act[0].set_acted(True)
                if act[0].get_job_name() == 'Werewolf':
                    attacked_player = act[1]
                await client.get_user(act[0].get_id()).send(text)
                # print(act[1].get_name())
            act_stack.clear()
            print(text)
            time.sleep(3)

            #パン屋の生死判定
            global bakery_flag
            for p in players:
                if (p.get_job_name() == 'Bakery' and not p.is_dead()):
                    bakery_flag = True
                    break
            if bakery_flag:
                await message.channel.send('パン屋さんが美味しいパンを作ってくれました。')

            await message.channel.send('朝が来ました。')
            text = ''
            for p in players:
                p.morning()
            if attacked_player.is_dead():
                text += '昨夜は ' + attacked_player.get_name() + ' さんが死にました。'
            else:
                text += '昨夜は誰も死にませんでした'
            await message.channel.send(text)

# 終了処理
            text = ''
            villager_cnt = 0
            wolf_cnt = 0
            for p in players:
                if not(p.is_dead()):
                    if p.get_is_wolf():
                        wolf_cnt += 1
                    else:
                        villager_cnt += 1
            if wolf_cnt >= villager_cnt:
                text += '\n勝者:'
                for p in players:
                    if p.get_is_side() == 0:                            
                        text += p.getname() + '\n'
                text += '人狼の勝ちです。'
            if wolf_cnt == 0:
                text += '\n勝者:'
                for p in players:
                    if p.get_is_side() == 0:
                        text += p.get_name() + '\n'
                text += '村人の勝ちです。'
            await message.channel.send(text)

    if args[0] == 'resetj':
        players.clear()

    if args[0] == 'inctcnt':
        target_count += 1
        await message.channel.send('Debug用関数です。')

    if args[0] == 'help':
        text = ' ```\ngetm:\n    参加可能メンバーを表示\nsetp <name1> <name2> ... <nameN>:\n    参加メンバーを設定 引数は getm で得た名前\nsetj <job1>:<num1> <job2>:<num2> ... <jobN>:<numN>:\n    役職を設定 引数は<役職の名前>:<その役職の人数>\ngamestart:\n    役職を割り振ってゲームスタート\ngetjob:\n    自分の役職を確認 dmでbotから役職が届く\nvote <name>:\n    引数の名前の人に投票する\nvotend:\n    投票を締め切って投票結果を表示\nact:\n    夜のアクションをする dmで次の指示が届く\ntarget <name>:\n    botに対してdmで送る \n    引数の名前の人に対して夜のアクションを起こす e.g. 人狼であればその人を噛む 狩人であればその人を護る\n    全員のアクションが終わると順番にアクションが実行され朝が来る\nhelp:\n   このメッセージを表示```'
        await message.channel.send(text)
client.run(TOKEN)
