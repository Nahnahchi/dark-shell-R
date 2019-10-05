class Scripts:

    ITEM_DROP = "mov ebp, %s\n" \
                "mov ebx, %s\n" \
                "mov ecx, 0xFFFFFFFF\n" \
                "mov edx, %s\n" \
                "mov eax, [%s]\n" \
                "mov [eax + 0x828], ebp\n" \
                "mov [eax + 0x82C], ebx\n" \
                "mov [eax + 0x830], ecx\n" \
                "mov [eax + 0x834], edx\n" \
                "mov eax, [%s]\n" \
                "push eax\n" \
                "call %s\n" \
                "ret\n"

    ITEM_GET = "mov edi, %s\n" \
               "mov ecx, %s\n" \
               "mov esi, %s\n" \
               "mov ebp, %s\n" \
               "mov ebx, 0xFFFFFFFF\n" \
               "push 0x0\n" \
               "push 0x1\n" \
               "push ebp\n" \
               "push esi\n" \
               "push ecx\n" \
               "push edi\n" \
               "call %s\n" \
               "ret\n"

    BONFIRE_WARP = "mov esi, [%s]\n" \
                   "mov edi, 0x1\n" \
                   "push edi\n" \
                   "call %s\n" \
                   "ret\n"

    LEVEL_UP = "mov eax, %s\n" \
               "mov ecx, %s\n" \
               "call %s\n" \
               "ret\n"
