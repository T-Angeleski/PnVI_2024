extends Area3D

signal collected

func _ready():
	add_to_group("treasures")

func _process(delta):
	rotate_y(1.5 * delta)

func _on_body_entered(body):
	if body is CharacterBody3D:
		collected.emit()
		queue_free()
