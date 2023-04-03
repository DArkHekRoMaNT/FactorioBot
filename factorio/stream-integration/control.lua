script.on_init(function()
	game.print("Stream Integration started!", { r = 255, g = 215, b = 0, a = 1 })
end)

function get_player(player_name)
	if not player_name then
		game.print("Add player name")
		return
	end

	local player = game.get_player(player_name)
	if not player then
		game.print("Unknown player "..player_name)
		return
	end

	return player
end

function get_random_position_around(player, radius)
	local offset_x = radius - math.random(1, radius * 2)
	local offset_y = radius - math.random(1, radius * 2)
	return {
		x = player.position.x + offset_x,
		y = player.position.y + offset_y
	}
end

function spawn_units_from_spawner(name, quantity, handler)
	local spawner = game.entity_prototypes[name]
	local evolution_factor = game.forces.enemy.evolution_factor

	local enemies = {}
	local total_weight = 0
	for _, unit_data in ipairs(spawner.result_units) do
		local enemy_weight = 0
		local last_point
		local point
		for _, spawn_point in ipairs(unit_data.spawn_points) do
			last_point = point
			point = spawn_point
			if spawn_point.evolution_factor > evolution_factor then
				break
			end
		end

		if evolution_factor <= point.evolution_factor and last_point then
			local weight_diff = point.weight - last_point.weight
			local factor_diff = point.evolution_factor - last_point.evolution_factor
			local ratio = (evolution_factor - last_point.evolution_factor) / factor_diff
			enemy_weight = last_point.weight + weight_diff * ratio
		else
			enemy_weight = point.weight
		end

		if enemy_weight > 0 then
			total_weight = total_weight + enemy_weight
			table.insert(enemies, { unit = unit_data.unit, weight = enemy_weight })
		end
	end

	for i=1, quantity do
		local random_weight = math.random() * total_weight
		for _, enemy in ipairs(enemies) do
			random_weight = random_weight - enemy.weight
			if random_weight <= 0 then
				handler(enemy.unit)
			end
		end
	end
end

commands.add_command("spawn_biters", "summon biters around you", function(command)
	local player = get_player(command.parameter)
	if not player then
		return
	end

	spawn_units_from_spawner("biter-spawner", 10,function(unit)
		local surface = player.surface
		local position = surface.find_non_colliding_position(unit, get_random_position_around(player, 10), 10, 1)
		if position then
		  surface.create_entity({ name = unit, position = position, force = game.forces.enemy })
		end
	end)

	player.print("Good luck to survive", { r = 255, g = 0, b = 0, a = 1 })
end)

commands.add_command("spawn_splitters", "summon splitters around you", function(command)
	local player = get_player(command.parameter)
	if not player then
		return
	end

	spawn_units_from_spawner("spitter-spawner", 10,function(unit)
		local surface = player.surface
		local position = surface.find_non_colliding_position(unit, get_random_position_around(player, 10), 10, 1)
		if position then
		  surface.create_entity({ name = unit, position = position, force = game.forces.enemy })
		end
	end)

	player.print("Good luck to survive", { r = 255, g = 0, b = 0, a = 1 })
end)

commands.add_command("spawn_worms", "summon worms around you", function(command)
	local player = get_player(command.parameter)
	if not player then
		return
	end

	local name
	local evolution = game.forces.enemy.evolution_factor
	if evolution > 0.9 then
		name = "behemoth-worm-turret"
	elseif evolution > 0.5 then
		name = "big-worm-turret"
	elseif evolution > 0.3 then
		name = "medium-worm-turret"
	else
		name = "small-worm-turret"
	end

	for i = 1, 5 do
		local surface = player.surface
		local position = surface.find_non_colliding_position(name, get_random_position_around(player, 10), 10, 1)
		if position then
			surface.create_entity({ name = name, position = position, force = game.forces.enemy })
		end
	end

	player.print("Good luck to survive", { r = 255, g = 0, b = 0, a = 1 })
end)

commands.add_command("spawn_spawners", "summon spawners around you", function(command)
	local player = get_player(command.parameter)
	if not player then
		return
	end

	for i = 1, 5 do
		local unit
		if math.random() < 0.5 then
			unit = "spitter-spawner"
		else
			unit = "biter-spawner"
		end
		local surface = player.surface
		local position = surface.find_non_colliding_position(unit, get_random_position_around(player, 10), 10, 1)
		if position then
			surface.create_entity({ name = unit, position = position, force = game.forces.enemy })
		end
	end

	player.print("Good luck to survive", { r = 255, g = 0, b = 0, a = 1 })
end)

