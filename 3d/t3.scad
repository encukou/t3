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
            translate ([-24, -115, h]) cube ([50-2, 100, 100]);
            translate ([0, 5, 0]) rotate ([0, 0, -135]) cube ([100, 100, 100]);
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

module headers (n=5) {
    rotate ([0, 0, 45]) translate ([23, -3*n-3, 1+eps]) cube ([12, 3*n, 3]);
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
                translate ([0, 27, 0]) cylinder (8, d=17);
                // Screw Base
                screw_mod (9);
                // Button Supports
                buttons(9);
                // Header Support
                rotate ([0, 0, 45]) translate ([24, -22, 1+eps]) cube ([3, 22, 4]);
            }
            // Speaker hole
            translate ([0, 27, 0]) {
                translate ([0, 0, 1]) cylinder (100, d=15.5);
                translate ([0, 0, -1]) cylinder (100, d=5, $fn=10);
                for (i=[0:8]) rotate([0, 0, 360/8*i]) {
                    translate ([5, 0, -1]) cylinder (100, d=1.5, $fn=10);
                }
            }
            // Wire paths
            translate ([0, 0, 0.25]) wire_paths (0.751);
            // Small Wall Adjustment
            wall_adjust (2);
            // Screw Holes
            translate ([0, 0, -1]) screw_mod (100, SCREW_R);
            // Header Holes
            headers (5);
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
            translate ([-0.5, -35, 1]) cube ([1, 100, 100]);
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
                screw_mod (3);
                translate ([-15-1, -15-1, 0]) cube ([30+2, 30+2, 3]);
                buttons (2, 1);
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
    translate ([0, 27, 1]) cylinder (7, d=14);
    // Headers
    headers ();
    // Buttons
    translate ([0, 0, 9]) buttons ();
    // Screen
    translate ([0, 0, 9]) {
        for (x=[-1,0,1]) for (y=[-1,0,1]) {
            translate ([x*9, y*9, 0]) {
                cylinder (1, d=9);
                translate ([-2.5, -2.5, 0]) cube ([5, 5, 2.5]);
            }
        }
    }
}

% extra_parts ();
