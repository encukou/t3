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
    translate ([0, 0, -100]) screw_mod (200, 2);
}

module button (h, minus) {
    translate ([-minus, -minus, 0]) cube ([6+minus*2, 6+minus*2, h]);
}

module buttons (h=3, minus=0) {
    // Cross
    translate ([-27.5, 0, 0]) for (r=[0:90:360-1]) {
        rotate ([0, 0, r]) translate ([0, 2, 0]) rotate ([0, 0, 45]) button (h, minus);
    }
    // AB
    translate ([20-1, -2, 0]) rotate ([0, 0, -45]) button (h, minus);
    translate ([35+1, 2, 0]) rotate ([0, 0, 90+45]) button (h, minus);
}

module switch (h=7, minus=0) {
    translate ([-5-minus, 35-minus, 0]) cube ([10+minus*2, 3+minus*2, h]);
}

module t3_battery_holder () {
    n=2;
    difference () {
        intersection () {
            main_octagon (6-0.2);
            union () {
                translate ([-15+0.1, -15+30+0.1, -1]) cube ([30-0.2, 30, 100]);
                translate ([-40, -15+45, -1]) cube ([80, 30, 100]);
            }
        }
        translate ([0, 25, -1]) cylinder (100, d=20+1);
    }
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
                translate ([0, 27, 0]) cylinder (9, d=18);
                // Screw Base
                screw_mod (7);
                // Button Supports
                buttons(9);
                // Switch Support
                translate ([-7, 37.5, 0]) cube ([14, 2, 9]);
                // Header Support
                rotate ([0, 0, 45]) translate ([23.5, -22, 1+eps]) cube ([3, 22, 4]);
                // Battery Support
                intersection () {
                    main_octagon (2);
                    union () {
                        translate ([-100, -40, 0]) cube ([200, 15, 2]);
                        translate ([-15, -40, 0]) cube ([30, 25, 2]);
                    }
                }
                // ESP-12 Support
                translate ([-8, -12, 0]) cube ([3, 4, 5]);
                translate ([5, -12, 0]) cube ([3, 4, 5]);
                translate ([-10, 12, 0]) cube ([4, 4, 5]);
                translate ([6, 12, 0]) cube ([4, 4, 5]);
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
            translate ([0, 0, 1.01]) {
                translate ([ 4-0.5, -35, 0]) cube ([1, 22, 1]);
                translate ([-4-0.5, -35, 0]) cube ([1, 22, 1]);
            }
            // Small Wall Adjustment
            translate ([-24, -110, 8]) cube ([50-2, 100, 100]);
            // Screw Holes
            translate ([0, 0, -1]) screw_mod (100, SCREW_R);
            // Header Holes
            headers (5);
            // Fun Holes
            translate ([0, 0, -1]) buttons(2, -2.5);
            // Switch Support
            translate ([0, 0, 6.5]) switch(100, 0.5);
            // ESP-12 Support
            translate ([-8-0.5, -10-0.5, 4]) cube ([16+1, 24+1, 100]);
        }
    }
}

module t3_battery_cover () {
    union () {
        difference () {
            intersection () {
                union () {
                    main_octagon (1);
                }
                translate ([-25+1.5, -115, -1]) cube ([50-3, 100, 100]);
                translate ([0, 5, 0]) rotate ([0, 0, -135]) cube ([100, 100, 100]);
            }
            screw_holes ();
            translate ([-0.5, -35, 0.5]) cube ([1, 100, 100]);
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
                // Screen Hole Wall
                translate ([-15-1, -15-1, 0]) cube ([30+2, 30+2, 3]);
                // Button Hole Walls
                buttons (2, 1.5);
                // Switch Hole Wall
                translate ([0, 0, 0]) switch(3, 2);
            }
            screw_holes ();
            // Screen Hole
            translate ([-15, -15, -1]) cube ([30, 30, 100]);
            // Button Holes
            translate ([0, 0, -1]) buttons (100, 0.25);
            // Switch Hole
            translate ([0, 0, -1]) switch(100, 0.5);
        }
    }
}

module t3_display_holder () {
    union () {
        difference () {
            union () {
                translate ([-16, -14, 0]) cube ([32, 30, 2]);
                for (x=[-1,1]) for (y=[-1,1]) scale([x, y, 1]) {
                    translate ([20, 20, 0]) cylinder (1, r=4, $fn=10);
                    translate ([16, 14, 0]) cube ([8, 6, 1]);
                    translate ([24, 14, 0]) rotate ([0, 0, 45])
                        translate ([-20, 0, 0]) cube ([20, 4*sqrt(2), 1]);
                }
            }
            for (x=[-1,0,1]) for (y=[-1,0,1]) {
                translate ([9.3*x, 9.3*y, -1]) cylinder (4, r=5.5);
            }
            screw_holes ();
        }
        for (y=[-3,-1,1,3]) {
            translate ([-15, 4.5*y-0.5, 0]) cube ([30, 1, 1]);
        }
    }
}

union () {
    translate ([0, 0, 0]) t3_base ();
    translate ([70, 0, 0]) t3_battery_cover ();
    translate ([70, 20, 0]) t3_display_holder ();
    translate ([70, 40, 0]) t3_battery_holder ();
    translate ([0, 85, 0]) scale ([-1, 1, 1]) t3_top ();
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
    // Screen Holder
    translate ([0, 0, 7]) t3_display_holder ();
    // Screen
    translate ([0, 0, 8]) {
        for (x=[-1,0,1]) for (y=[-1,0,1]) {
            translate ([x*9, y*9, 0]) {
                cylinder (1, d=9);
                translate ([-2.5, -2.5, 0]) cube ([5, 5, 2.5]);
            }
        }
    }
    // Switch
    translate ([0, 0, 7]) switch(5);
    // ESP-12
    translate ([-8, -10, 4]) {
        cube ([16, 24, 1]);
        translate ([2, 1, 0]) cube ([12, 15, 3]);
    }
}

% extra_parts ();
