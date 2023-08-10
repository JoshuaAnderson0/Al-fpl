def get_allowed_max_of_type(player_type: int) -> int:
    match player_type:
        case 1:
            return 2
        case 2:
            return 5
        case 3:
            return 5
        case 4:
            return 3


def get_type_name(player_type: int) -> str:
    match player_type:
        case 1:
            return 'Goalkeeper'
        case 2:
            return 'Defender'
        case 3:
            return 'Midfielder'
        case 4:
            return 'Forward'
