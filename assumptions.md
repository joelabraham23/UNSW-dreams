Stephen: 
If a user joins a channel they are already in, they will remain in the channel and no error will be raised.

Assumed messages can be made up from 1 to 1000 of ANY character (Else will result in InputError).

When sharing a message, the original + formatting + new message also cannot exceed 1000 words.

Assumed for the search that case of letters does not matter and can be ignored.


Toby:

When functions channels_list and channels_listall are called, public and private channels will be printed. 

The channel_list and channel_listall function will return a dictionary with the key 'channels' in the following format, {'channels' :[{'channel_id': id, 'name':}]}.

AccessError is the only exception for channel_list_v1 and channel_listall_v1

When inviting a user that is already a member of a DM, it will not attempt to add them again, creating duplicate members. 

Is it guaranteed that the dm_create tests will not have a scenario where the dm_creator is in the 'u_ids'

The creator of a DM, can be removed from their own DM. Additionally, a DM with no members will still exist.

'dm_list_v1' will return the dm's in the format
'dms': [{'dm_id': dm_id, 'name': channel_name}]

Removing a DM removes all its contents completely, making it untraceable.


Joel:

Another assumption made was that the user will not be logging in twice.
An assumption I made was that the first and last name were to contain only alphabetical characters. 

This was assumed since it wasn't indicated in spec but seems appropriate to have as a restriction for when registering a user.



Akshayram:

Assumed that if user was invalid it outputs an Access Error

Assumed that all members contains owner members.



Jefferson: 

Creating the channel name would not be unique and can be used by any other users trying to create a channel name even if setting as a public channel.

Functions such as user login would not be stored in the data and would not require resetting.

When a user leaves a dm (dm_leave), their handle will be taken away from the dm_handle