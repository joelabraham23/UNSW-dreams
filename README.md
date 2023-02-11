# COMP1531 Major Project

 **✨ Teamwork makes the [UNSW] Dream[s] work 🌈**

To manage the transition from trimesters to hexamesters in 2020, UNSW has established a new focus on building an in-house digital collaboration and communication tool for groups and teams to support the high intensity learning environment.

Rather than re-invent the wheel, UNSW has decided that it finds the functionality of **<a href="https://www.microsoft.com/en-au/microsoft-teams/group-chat-software">Microsoft Teams</a>** to be nearly exactly what it needs. For this reason, UNSW has contracted out Penguin Pty Ltd (a small software business run by Hayden) to build the new product. In UNSW's attempt to try and add a lighter not to the generally fatigued and cynical student body, they have named their UNSW-based product **UNSW Dreams** (or just **Dreams** for short). **UNSW Dreams** is the communication tool that allows you to share, communication, and collaborate to (attempt to) make dreams a reality.

Penguin Pty Ltd has sub-contracted two software firms:

* BlueBottle Pty Ltd (two software developers, Andrea and Andrew, who will build the initial web-based GUI)
* YourTeam Pty Ltd (a team of talented misfits completing COMP1531 in 21T1), who will build the backend python server and possibly assist in the GUI later in the project

In summary, UNSW contracts Penguin Pty Ltd, who sub contracts:

* BlueBottle (Andrea and Andrew) for front end work
* YourTeam (you and others) for backend work

Penguin Pty Ltd met with Andrea and Andrew (the front end development team) 2 weeks ago to brief them on this project. While you are still trying to get up to speed on the requirements of this project, Andrea and Andrew understand the requirements of the project very well.

Because of this they have already specified a **common interface** for the frontend and backend to operate on. This allows both parties to go off and do their own development and testing under the assumption that both parties will comply with the common interface. This is the interface **you are required to use**

Besides the information available in the interface that Andrea and Andrew provided, you have been told (so far) that the features of **Dreams** that UNSW would like to see implemented include:

1. Ability to login, register if not registered, and log out
2. Ability to reset password if forgotten
3. Ability to see a list of channels
4. Ability to create a channel, join a channel, invite someone else to a channel, and leave a channel
5. Within a channel, ability to view all messages, view the members of the channel, and the details of the channel
6. Within a channel, ability to send a message now, or to send a message at a specified time in the future
7. Within a channel, ability to edit, share between channels, remove, pin, unpin, react, or unreact to a message
8. Ability to view anyone's user profile, and modify a user's own profile (name, email, handle, and profile photo)
9. Ability to search for messages based on a search string
10. Ability to modify a user's admin permissions: (MEMBER, OWNER)
11. Ability to begin a "standup", which is an X minute period where users can send messages that at the end of the period will automatically be collated and summarised to all users
12. Ability to send message directly to a user (or group of users) via direct messaging (DM).

The specific capabilities that need to be built for this project are described in the interface at the bottom. This is clearly a lot of features, but not all of them are to be implemented at once (see below)
