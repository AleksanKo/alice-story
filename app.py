import json
import re
from alice_scripts import Skill, request, say, suggest
skill = Skill(__name__)

def replace_tags_and_brackets(content):
    filtered_content = content.replace('<p>', '').replace('</p>', '')\
                                .replace('&lt;', '').replace('&gt;', '').replace('<br>', '')\
                                .replace('speaker audio=','')

    filtered_content = re.sub(r'\".*\"', '', filtered_content)
    print(filtered_content)
    return filtered_content

def get_children_buttons(node):
    buttons = []
    for i in elements[node]['outputs']:
        buttons.append(replace_tags_and_brackets(connections[i]['label']))
    return buttons

def search_for_audio(content):
    try:
        audio_link = re.search(r'\"(.*)\"', content).group(1)
        print(audio_link)
    except AttributeError:
        audio_link = ''
    return audio_link

def get_children_connections(node):
    children_connections = {}
    for i in elements[node]['outputs']:
        try:
            children_connections.update({replace_tags_and_brackets(connections[i]['label']):
                                             jumpers[connections[i]['targetid']]['elementId']})
        except KeyError:
            children_connections.update({replace_tags_and_brackets(connections[i]['label']): connections[i]['targetid']})
    print(children_connections)
    return children_connections

with open('project_settings.json', 'r') as p:
    all_data = json.loads(p.read())

starting_element = all_data['startingElement']
connections = all_data['connections']
elements = all_data['elements']
jumpers = all_data['jumpers']
beginning = replace_tags_and_brackets(elements[starting_element]['content'])
#print(elements[starting_element]['content'])
#print(elements[connections[elements[starting_element]['outputs'][0]]['targetid']]['title'])
#print(beginning['outputs'])

@skill.script
def run_script():
    yield say(beginning,
              suggest(*get_children_buttons(starting_element)))

    children_connections = get_children_connections(starting_element)
    following_element = request.command
    try:
        yield say(replace_tags_and_brackets(elements[children_connections[following_element]]['content']),
              suggest(*get_children_buttons(children_connections[following_element])))
    except KeyError:
        yield say('Я вас не поняла. Выберите один из вариантов:',
                  suggest(*get_children_buttons(children_connections[following_element])))
        print(following_element)
        print(children_connections)

    while children_connections:
        children_connections = get_children_connections(children_connections[following_element])
        following_element = request.command
        if following_element in children_connections:
            yield say(replace_tags_and_brackets(elements[children_connections[following_element]]['content']),
                  suggest(*get_children_buttons(children_connections[following_element])),
                  tts=search_for_audio(elements[children_connections[following_element]]['content']))
        else:
            yield say('Я вас не поняла. Выберите один из вариантов')
            print(following_element)
            print(children_connections)

    yield say('Спасибо за игру!',
              end_session=True)
