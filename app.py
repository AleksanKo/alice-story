import json
import re
from alice_scripts import Skill, request, say, suggest
skill = Skill(__name__)

def replace_tags(content):
    return content.replace('<p>','').replace('</p>','')

def get_children_buttons(node):
    buttons = []
    for i in elements[node]['outputs']:
        buttons.append(replace_tags(connections[i]['label']))
    return buttons

def search_for_audio(content):
    pass

def get_children_connections(node):
    children_connections = {}
    #print(elements[node]['outputs'])
    for i in elements[node]['outputs']:
        try:
            children_connections.update({replace_tags(connections[i]['label']):
                                             jumpers[connections[i]['targetid']]['elementId']})
        except KeyError:
            children_connections.update({replace_tags(connections[i]['label']): connections[i]['targetid']})
    print(children_connections)
    return children_connections

with open('project_settings.json', 'r') as p:
    all_data = json.loads(p.read())
starting_element = all_data['startingElement']
connections = all_data['connections']
elements = all_data['elements']
jumpers = all_data['jumpers']
beginning = replace_tags(elements[starting_element]['content'])
#print(elements[starting_element]['content'])
#print(elements[connections[elements[starting_element]['outputs'][0]]['targetid']]['title'])
#print(beginning['outputs'])


@skill.script
def run_script():
    yield say(beginning,
              suggest(*get_children_buttons(starting_element)))

    following_element = request.command

    children_connections = get_children_connections(starting_element)
    #print(children_connections)
    #print(elements[children_connections[following_element]])
    #в цикл это все

    yield say(replace_tags(elements[children_connections[following_element]]['content']),
              suggest(*get_children_buttons(children_connections[following_element])))

    while children_connections :
        children_connections = get_children_connections(children_connections[following_element])
        following_element = request.command
        #print(elements[children_connections[following_element]]['content'])
        yield say(replace_tags(elements[children_connections[following_element]]['content']),
                  suggest(*get_children_buttons(children_connections[following_element])),
                  tts='alice-sounds-things-door-2.opus')

    #yield say('Сколько вам лет?')
    #while not request.matches(r'\d+'):
        #yield say('Я вас не поняла. Скажите число')
    #age = int(request.command)

    yield say('Рада',
              end_session=True)
