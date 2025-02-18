extends Node

var score := 0
var total_treasures := 0
var time_remaining := 60 * 2
var game_active := true
var treasure_scene

@export var timer_label: Label
@export var score_label: Label
@export var game_over_panel: Panel
@export var game_timer: Timer
@export var treasure_spawn_points: Node3D

func _ready():
	treasure_scene = preload("res://scenes/treasure/treasure.tscn")
	spawn_treasures()
	game_timer.start()

func spawn_treasures():
	var spawn_points = treasure_spawn_points.get_children()
	
	for point in spawn_points:
		var treasure = treasure_scene.instantiate()
		add_child(treasure)
		treasure.global_position = point.global_position
		treasure.connect("collected", _on_treasure_collected)
		total_treasures += 1
	
	score_label.text = "Treasures: 0/" + str(total_treasures)

func _on_treasure_collected():
	score += 1
	score_label.text = "Treasures: " + str(score) + "/" + str(total_treasures)
	
	if score >= total_treasures:
		game_over(true)

func _on_game_timer_timeout():
	if not game_active:
		return
		
	time_remaining -= 1
	var minutes = time_remaining / 60
	var seconds = time_remaining % 60
	timer_label.text = "Time: %d:%02d" % [minutes, seconds]
	
	if time_remaining <= 0:
		game_over(false)

func game_over(victory: bool):
	game_active = false
	game_over_panel.show()
	var message = "Victory!, press R to restart" if victory else "Time's Up!, press R to restart"
	game_over_panel.get_node("MessageLabel").text = message

func _input(event):
	if event.is_action_pressed("restart"):
		get_tree().reload_current_scene()
