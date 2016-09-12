eps = 0.001;
SCREW_R = 1.25;

module main_octagon (h, minus=0) {
    m = minus;
    union () {
        intersection () {
            translate ([-40+m, -40+m, 0]) cube ([80-m*2, 80-m*2, h]);
            rotate ([0, 0, 45]) translate ([-35+m, -35+m, 0]) cube ([70-m*2, 70-m*2, h]);
        }
    }
}

module the_wall (h, minus=0) {
    m = minus;
    difference () {
        main_octagon (h, m);
        translate ([-50, -55+m, 0]) cube ([100, 30, h+1]);
        translate ([-15-m, -45-m, 0]) cube ([30+2*m, 30+2*m, h+1]);
    }
}

module screw_mod (h, r=3) {
    for (x=[-20, 20]) {
        for (y=[-20, 20]) {
            translate ([x, y, 0]) cylinder (h, r=r, $fn=10);
        }
    }
}

module screw_holes () {
    translate ([0, 0, -100]) screw_mod (200, 1.75);
}

module wall_adjust (n) {
    h = 1+3*n;
    difference () {
        intersection () {
            translate ([-24, -105, h]) cube ([50-2, 100, 100]);
            translate ([0, 10, 0]) rotate ([0, 0, -135]) cube ([100, 100, 100]);
        }
    }
}

module wire_paths (h) {
    union () {
        for (s=[-1, 1]) {
            translate ([-0.5+4*s, -35, 0]) cube ([1, 35, h]);
            translate([0, -10, 0]) rotate ([0, 0, 45*s])
                translate ([-6, -0.5, 0]) cube ([12, 1, h]);
        }
    }
}

module button (h, minus) {
    translate ([-minus, -minus, 0]) cube ([6+minus*2, 6+minus*2, h]);
}

module buttons (h=3, minus=0) {
    // Cross
    translate ([-38, -3, 0]) button (h, minus);
    translate ([-23, -3, 0]) button (h, minus);
    translate ([-30.5, -10.5, 0]) button (h, minus);
    translate ([-30.5, 4.5, 0]) button (h, minus);
    // AB
    translate ([20, -4, 0]) button (h, minus);
    translate ([29, -2, 0]) button (h, minus);
}

module t3_base () {
    union () {
        difference () {
            union () {
                // Base Plate
                main_octagon (1);
                // Perimeter Wall
                difference () {
                        the_wall (9, 0);
                    the_wall (100, 1);
                }
                // Speaker wall
                translate ([0, 27, 0]) cylinder (7, d=17);
                // Screw Base
                screw_mod (7);
            }
            // Speaker hole
            translate ([0, 27, -1]) cylinder (100, d=15.5);
            // Wire paths
            translate ([0, 0, 0.25]) wire_paths (0.751);
            // Small Wall Adjustment
            wall_adjust (2);
            // Screw Holes
            translate ([0, 0, -1]) screw_mod (100, SCREW_R);
            // Header Holes
            translate ([28, -3*5/2, 1+eps]) cube ([100, 3*5, 3]);
        }
    }
}

module t3_battery_cover () {
    union () {
        difference () {
            intersection () {
                union () {
                    main_octagon (2-eps);
                }
                wall_adjust (-1);
            }
            screw_holes ();
            translate ([0, -1, 1]) wire_paths (1);
            // Capacitor Hole
            translate ([5, -13.5, -2]) cube ([12.5, 5, 5]);
            // Wire to Cap
            translate ([0, -11.5, 1]) cube ([10, 1, 1]);
            // Diode Hole
            translate ([-13, -12.5, -2]) cube ([7, 3, 5]);
            // Wire from Diode
            translate ([-16, -11.5, -0.75]) cube ([5, 1, 2]);
            // Hole Out
            translate ([-16, -11, -2]) cylinder (5, r=1, $fn=10);
        }
    }
}

module t3_top () {
    union () {
        difference () {
            union () {
                difference () {
                    main_octagon (3);
                    translate ([0, 0, 1]) main_octagon (100, 1);
                }
                screw_mod (2);
                translate ([-15-1, -15-1, 0]) cube ([30+2, 30+2, 2]);
                buttons (3, 1);
            }
            screw_holes ();
            translate ([-15, -15, -1]) cube ([30, 30, 100]);
            translate ([0, 0, -1]) buttons (100, 0.25);
        }
    }
}

union () {
    translate ([0, 0, 0]) t3_base ();
    translate ([70, 0, 0]) t3_battery_cover ();
    translate ([0, 85, 0]) scale ([-1, 1, 1]) t3_top (1);
}

module extra_parts () {
    // Bat cover
    translate ([0, 0, 9]) rotate ([0, 180, 0]) t3_battery_cover ();
    // Speaker
    translate ([0, 27, 0]) cylinder (7, d=14);
    // Headers
    translate ([28, -3*5/2, 1+eps]) cube ([12, 3*5, 3]);
    // Buttons
    translate ([0, 0, 9]) buttons ();
}

% extra_parts ();
