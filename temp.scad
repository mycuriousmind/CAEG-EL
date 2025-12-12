union() {
	cylinder($fn = 6, h = 5.0, r = 10.0);
	translate(v = [0, 0, 5.0]) {
		cylinder($fn = 64, h = 30.0, r = 5.0);
	}
}
