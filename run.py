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

jobs = ['Werewolf', 'Seer', 'Villager', 'Knight']
job_setting = {'Werewolf': 0, 'Seer': 0, 'Villager': 0, 'Knight': 0}
job_name = {'Werewolf': '人狼', 'Seer': '占い師', 'Villager': '村人', 'Knight': '狩人'}
job_priority = {'Werewolf': 0, 'Seer': 1, 'Villager': 2, 'Knight': 3}

act_stack = []
target_count = 0


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

        for i in range(len(game_members)):
            p = Player(game_members[i][0], game_members[i][1], js[i])
            players.append(p)

        # debug
        text += '\n debug'
        for p in players:
            text += '\n - ' + p.get_name() + ': ' + p.get_job()

        await message.channel.send(text)

    if args[0] == 'getjob':
        text = 'あなたの役職は '
        for p in players:
            if message.author.id == p.get_id():
                text += p.get_job() + ' です。'
        await message.author.send(text)

    if args[0] == 'vote':
        text = ''
        for p in players:
            if p.get_id() == message.author.id:
                for p2 in players:
                    if args[1] == p2.get_name() and not(p.is_voted()):
                        p.vote(p2)
                        text += p.get_name() + ' さんは ' + p2.get_name() + ' さんに投票しました。'

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
                await client.get_user(act[0].get_id()).send(text)
                # print(act[1].get_name())
            act_stack.clear()
            print(text)
            time.sleep(3)
            await message.channel.send('朝が来ました。')
            text = '昨夜は '
            for p in players:
                p.morning()
                if p.is_dead():
                    text += p.get_name() + ' さんが死にました。'
            if text == '昨夜は':
                text += '誰も死にませんでした'
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
                text += '人狼の勝ちです。'
            if wolf_cnt == 0:
                text += '村人の勝ちです。'
            await message.channel.send(text)

    if args[0] == 'resetj':
        players.clear()

    if args[0] == 'inctcnt':
        target_count += 1
        await message.channel.send('Debug用関数です')
client.run(TOKEN)
