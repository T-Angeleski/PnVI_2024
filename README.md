# Park Treasure Hunt - Game Documentation  

Теодор Ангелески 211080

## Преглед  
**Park Treasure Hunt** е first-person 3D игра развиена во **Godot 4.x**, каде што играчот истражува парк средина за да собере богатства пред да истече времето. Играта вклучува физички базирано движење, камера од прво лице и кориснички интерфејс за следење на резултатот и времето.  

---

## Основни системи  

### Player Controller  
- Имплементира **движење од прво лице** и **контрола на камерата**  
- Користи **head bobbing** и **FOV прилагодување** за подобро искуство  

### Game Manager System  
- Го контролира **основниот тек на играта**, вклучувајќи **резултат, тајмер и услови за победа/пораз**  

### Treasure System  
- Имплементира **колекциони предмети** што играчот ги собира  
- Парите **се ротираат** за визуелен ефект  
- **Систем базиран на сигнали** за собирање предмети  

---

## Input System  
Играта користи следниве копчиња за контрола:  

| Акција        | Копче  |
|--------------|--------|
| Движење напред  | `W`  |
| Движење назад   | `S`  |
| Движење лево    | `A`  |
| Движење десно   | `D`  |
| Скок           | `Space`  |
| Трчање         | `Shift`  |
| Паузирање/излез | `Esc`  |
| Рестартирање   | `R`  |

---

## UI System  
Играта прикажува:  
- **Тековен резултат** (собрани/вкупно богатства)  
- **Преостанато време**  
- **Пораки за крај на играта (победа/пораз)**  

---

## Тек на играта  
1. Играта **почнува** со играчот поставен во парк средина  
2. **Тајмерот** започнува со одбројување од **2 минути**  
3. Играчот треба **да ги собере сите богатства** пред да истече времето  
4. Играта **завршува кога**:  
   - **Сите богатства се собрани** (**Победа**)  
   - **Истекува времето** (**Пораз**)  
5. Играчот може **да ја рестартира играта во секое време** со **копчето R**  


---

## Забелешки за имплементација  
- Развиена во **Godot 4.x**  
- **Физички базиран систем за движење**  
- **Комуникација меѓу сцените со користење на сигнали**  
- **Инстанцирање на сцени** за богатства  
- **Export variables** за лесна конфигурација  

---

## Документација на код  

### Player Controller (`player.gd`)  
Одговорен за **движење на играчот** и **контрола на камерата**  

#### Ефекти на камера  
```gdscript
const BOB_FREQ := 2.4  # Брзина на head bobbing ефектот
const BOB_AMP := 0.15  # Интензитет на bobbing ефектот
var t_bob := 0.0       # Временски акумулатор

const BASE_FOV := 75.0     # Основно видно поле
const FOV_CHANGE := 1.5    # Промена на видно поле при движење
```

#### Head Bobbing (Анимација при одење)  
```gdscript
func _headbob(time) -> Vector3:
    var pos = Vector3.ZERO
    pos.y = sin(time * BOB_FREQ) * BOB_AMP
    pos.x = cos(time * BOB_FREQ / 2) * BOB_AMP
    return pos
```
Создава природно движење на камерата при одење.  

#### Контрола на камера со глувче  
```gdscript
func _input(event):
    if event is InputEventMouseMotion:
        head.rotate_y(-event.relative.x * SENSITIVITY)
        camera.rotate_x(-event.relative.y * SENSITIVITY)
        camera.rotation.x = clamp(camera.rotation.x, deg_to_rad(-40), deg_to_rad(60))
```
Овозможува мазна контрола на погледот од прво лице.  

---

### Game Manager System (`game_manager.gd`)  
Контролира **состојбата на играта и логиката**  

#### Генерирање на богатства  
```gdscript
func spawn_treasures():
    var spawn_points = treasure_spawn_points.get_children()
    
    for point in spawn_points:
        var treasure = treasure_scene.instantiate()
        add_child(treasure)
        treasure.global_position = point.global_position
        treasure.connect("collected", _on_treasure_collected)
        total_treasures += 1
```
Создава богатства на однапред дефинирани локации и ги поврзува со системот за собирање.  

#### Тајмер систем  
```gdscript
func _on_game_timer_timeout():
    if not game_active: return
        
    time_remaining -= 1
    var minutes = time_remaining / 60
    var seconds = time_remaining % 60
    timer_label.text = "Time: %d:%02d" % [minutes, seconds]
    
    if time_remaining <= 0:
        game_over(false)
```
Ажурирање на времето и активирање на крај на играта ако времето истече.  

---

### Treasure System (`treasure.gd`)  
Имплементира **колекциони предмети кои ротираат и може да се соберат**  

#### Ротација за визуелен ефект  
```gdscript
func _process(delta):
    rotate_y(1.5 * delta)  # Ротира богатството со 1.5 рад/сек
```
Додава ефект на ротација за подобра видливост.  

#### Детекција на судир (Собирање богатства)  
```gdscript
func _on_body_entered(body):
    if body is CharacterBody3D:  # Проверува дали играчот го допира предметот
        collected.emit()         # Испраќа сигнал за собирање
        queue_free()             # Го отстранува предметот од сцената
```
Овозможува играчот да собира богатства.  

---

## Организација на сцената  

```
Game Scene
├── Player (CharacterBody3D)
│   ├── Head (Node3D)
│   │   └── Camera3D
│   └── CollisionShape3D
├── Environment
│   ├── Ground (StaticBody3D)
│   └── Park Objects (StaticBody3D)
├── TreasureSpawnPoints (Node3D)
└── UI (Control)
    ├── TimerLabel
    ├── ScoreLabel
    └── GameOverPanel
```

