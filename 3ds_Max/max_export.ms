(
	-- Create File ini
	
	userName = sysInfo.username 
	userFolder = @"C:\Users\" + userName
	
	iniFolder = userFolder + "\\m2b_materials\\"
	iniFileName = "m2b.ini"
	mainInfo = iniFolder + iniFileName
	
	--ini = iniFilePath
	
	-- Exist file to copy (remove from mzp)
	scriptFilePath = getThisScriptFilename()
	scriptFolder = getFilenamePath scriptFilePath
	iniInitPath = scriptFolder + "\\" + iniFileName
	
	
	if not (doesFileExist mainInfo) do
	(
		makeDir iniFolder all:true
		copyFile iniInitPath mainInfo
	)
	
	function cleanIni ini = 
	(
		for a in (getINISetting ini) do 
		(
			delIniSetting ini a
		)
	)
	
	function initIni = 
	(
		filePath = getFilenamePath maxfilepath
		modelName = getFilenameFile maxfilename
		
		iniFolder = "_" + (modelName) + "_import"
		iniFolderPath = filePath + iniFolder
		iniPathName = iniFolderPath + "\\" + modelName + ".ini"
		makeDir iniFolderPath
		if not (doesFileExist iniPathName) do
		(
			copyFile iniInitPath iniPathName
		)
		
		return iniPathName
	)
	
	-- Array for needed material parameters
	arrVrayMtlProps = #(
		"Diffuse",
		"reflection",
		"reflection_glossiness",
		"hilight_glossiness",
		"reflection_subdivs",
		"reflection_fresnel",
		"reflection_lockIOR",
		"reflection_IOR",
		"Refraction",
		"refraction_glossiness",
		"refraction_ior",
		"refraction_affectShadows",
		"refraction_affectAlpha",
		"refraction_fogColor",
		"refraction_fogMult",
		"refraction_subdivs",
		"brdf_type",
		"",
		"texmap_diffuse",
		"texmap_diffuse_multiplier",
		"texmap_reflection",
		"texmap_reflection_multiplier",
		"texmap_reflectionGlossiness",
		"texmap_reflectionGlossiness_multiplier",
		"texmap_reflectionIOR",
		"texmap_reflectionIOR_multiplier",
		"texmap_refraction",
		"texmap_refraction_multiplier",
		"texmap_refractionGlossiness",
		"texmap_refractionGlossiness_multiplier",
		"texmap_refractionIOR",
		"texmap_refractionIOR_multiplier"
		)
	
	struct _VrayMtl 
	(
		_main,
		_name = _main.name,
		_type = classof _main,
		diffuse_color = _main.Diffuse,
		reflection_color = _main.reflection,
		reflection_glossiness = _main.reflection_glossiness,
		hilight_glossiness = _main.hilight_glossiness,
		reflection_subdivs = _main.reflection_subdivs,
		reflection_fresnel = _main.reflection_fresnel,
		reflection_lockIOR = _main.reflection_lockIOR,
		reflection_IOR = _main.reflection_IOR,
		refraction_color = _main.refraction,
		refraction_glossiness = _main.refraction_glossiness,
		refraction_ior = _main.refraction_ior,
		refraction_affectShadows = _main.refraction_affectShadows,
		refraction_affectAlpha = _main.refraction_affectAlpha,
		refraction_fogColor = _main.refraction_fogColor,
		refraction_fogMult = _main.refraction_fogMult,
		refraction_subdivs = _main.refraction_subdivs,
		brdf_type = _main.brdf_type,
		bump_texture = _main.texmap_bump,
		texmap_bump_multiplier = _main.texmap_bump_multiplier,
		texmap_diffuse = _main.texmap_diffuse,
		texmap_diffuse_multiplier = _main.texmap_diffuse_multiplier,
		texmap_reflection = _main.texmap_reflection,
		texmap_reflection_multiplier = _main.texmap_reflection_multiplier,
		texmap_reflectionGlossiness = _main.texmap_reflectionGlossiness,
		texmap_reflectionGlossiness_multiplier = _main.texmap_reflectionGlossiness_multiplier,
		texmap_reflectionIOR = _main.texmap_reflectionIOR,
		texmap_reflectionIOR_multiplier = _main.texmap_reflectionIOR_multiplier,
		texmap_refraction = _main.texmap_refraction,
		texmap_refraction_multiplier = _main.texmap_refraction_multiplier,
		texmap_refractionGlossiness = _main.texmap_refractionGlossiness,
		texmap_refractionGlossiness_multiplier = _main.texmap_refractionGlossiness_multiplier,
		texmap_refractionIOR = _main.texmap_refractionIOR,
		texmap_refractionIOR_multiplier = _main.texmap_refractionIOR_multiplier
		
	)
	
	struct _NormalMap
	(
		_main,
		_name = _main.name,
		_type = classof _main,
		normalMap_texture = _main.normal_map,
		normalMap_multiplier = _main.normal_map_multiplier
	)
	
	struct _Bitmap
	(
		_main,
		_name = _main.name,
		_type = classof _main,
		texture = _main.fileName
	)
	
	fn defineStructure element = 
	(
		newStruct = case (classof element) of
		(
			VrayMtl: _VrayMtl (_main = element)
			VRayNormalMap: _NormalMap (_main = element)
			Bitmaptexture: _Bitmap (_main = element)
			default: undefined
		)
		
		return newStruct
	)
	
	fn fillDescription elem elemName iniPath= 
	(
		structToDescription = defineStructure elem
		
		for i in (getPropNames structToDescription) do
		(

			if (defineStructure (getProperty structToDescription i)) != undefined  and i != #_main then
			(
				setINISetting iniPath (toLower elemName) (toLower (i as string)) (toLower ("inner_attachment: " + ((getProperty structToDescription i) as string)))
				fillDescription (getProperty structToDescription i) (elemName + "\\\\" + (i as string)) iniPath
			)
			else
			(
				if (i != #_main) and (i != #_name) do
				(
					setINISetting iniPath (toLower elemName) (toLower (i as string)) (toLower ((getProperty structToDescription i) as string))
				)
			)
		)
	)
	
	-- Create and clean (if already created) model ini file
	ini = initIni()
	cleanIni ini
	
	
	-- Fill model ini File
	
	-- Materials
	for i in scenematerials do
	(
		setINISetting ini "Materials" i.name (classof i as string)
		fillDescription i i.name ini
	)
	
	-- Objects and layers
	for j in geometry do
	(
		setINISetting ini "Objects" j.name j.material.name
		setINISetting ini "Layers" j.name j.layer.name
	)
	
	-- Export model
	currentFbxVersion = FBXExporterGetParam "FileVersion"
	exportVersion = #FBX201200
	
	modelName = getFilenameFile maxfilename
	fbxModelPath = (getFilenamePath ini) + modelName + ".fbx"
	
	FBXExporterSetParam "FileVersion" exportVersion
	exportResult = exportFile fbxModelPath #noPrompt using:FBXEXP
	FBXExporterSetParam "FileVersion" currentFbxVersion
	
	
	-- Fill model name and path in main ini File
	if exportResult do
	(
		modelName = getFilenameFile maxfilename
		modelPath = maxfilepath + maxfilename
		
		newPath = substituteString modelPath "\\" "\\\\"
		
		setINISetting mainInfo "Models" modelName maxfilepath
	)
	
)