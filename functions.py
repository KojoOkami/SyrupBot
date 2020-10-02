def clean_msg(msg):
    msg_content = msg.clean_content
    new_content = ""
    parts = msg_content.replace("<", ">").split(">")
    for i in range(len(parts)):
        if i % 2 == 0:
            new_content += parts[i]
    return new_content


def check_bot_role(roles):
    for role in roles:
        if role.id == 740398217522446367:
            return True

    return False


async def value_message(message, last_message=''):
    clean_content = clean_msg(message).strip()
    # All Channels
    if len(clean_content) < 5:
        value = 1
    else:
        value = 3

    # Media, Art, Memes, NSFW, Creator Content
    if message.channel.id == 604535495640219700 or message.channel.id == 604832250403487755 or \
            message.channel.id == 604536055189864449 or message.channel.id == 710965849770426418 or \
            message.channel.id == 604534863223193601:
        if len(message.attachments) > 0:
            value = 5
        elif 'https://' in message.content:
            value = 5

    if ':SS_' in message.content:
        value += 3

    if len(message.mentions) > 0:
        value += 2

    if len(clean_content) > 400:
        value += 6

    if last_message == '':
        last_message = (await message.channel.history(limit=1, before=message.created_at).flatten())[0]
        if message.author != last_message.author:
            value += 1
    elif last_message is not None:
        if message.author != last_message.author:
            value += 1

    return value


def check_mod(roles):
    for role in roles:
        if role.id == 740391691055398982:
            return True
    return False


def check_admin(roles):
    for role in roles:
        if role.id == 740391690296361101:
            return True
    return False


def get_mention(member):
    return '@' + member.name + '#' + member.discriminator
