# DarkShellR
This is a command line multi-tool for testing and debugging DARK SOULS REMASTERED

Type `help` for the list of commands and `help [command]` to see the usage and available options.

Example of some of the commands:
```
set name Giant Dad
set covenant darkwraith
item-get grass-crest-shield 
item-get-upgrade zweihander
disable npc
warp oolacile-township bonfire
```

You can create custom items that you've modded into GameParams by either:
- Spawning it by ID: `item-get [category-name] [item-ID] [count]`
OR
- Adding it to the list of known items: `item-mod add`

To start reading performed animations use `get last-animation`.

To manage event flags type `enable [flag-id]` or `disable [flag-id]`, to read flags: `get [flag-id]`.

If you want to get notified when an event flag reaches one of its states, you can use the `on-flag notify` command.
You are also able to give yourself an item with `on-flag item-get [option]`.
`on-flag` should be able to take every single command as an argument even if they're not listed with autocomplete.
