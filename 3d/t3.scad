use <flexbatter.scad>

MAIN_W = 95;
MAIN_L = 120;
BOTTOM_L = 80;
MAIN_H = 19;
CHAM = 10;

SCREW_LOOSE_R = 1.9;
SCREW_SUPPORT_R = 3.5;
SCREW_TIGHT_R = 1.25;

SWITCH_W = 10;
SWITCH_L = 2.5;
SWITCH_H = 7;

SPEAKER_H = 7;
SPEAKER_R = 7;

TOP_L = MAIN_L - BOTTOM_L;

module main_footprint (h, offset=0) {
    o = offset;
    o2 = o * sqrt(2);
    rot_a=[0, 0, -45];
    rot_b=[0, 0, 135];
    wcham = MAIN_W/2-CHAM;
    difference () {
        translate ([-MAIN_W/2+o, -BOTTOM_L+o, 0]) cube ([MAIN_W-o*2, MAIN_L-o*2, h]);
        translate ([wcham-o2, -BOTTOM_L, -1]) rotate (rot_a) cube ([100, 100, 100]);
        translate ([-wcham+o2, -BOTTOM_L, -1]) rotate (rot_b) cube ([100, 100, 100]);
        translate ([wcham-o2, TOP_L, -1]) rotate ([0, 0, -45]) cube ([100, 100, 100]);
        translate ([-wcham+o2, TOP_L, -1]) rotate ([0, 0, 135]) cube ([100, 100, 100]);
    }
}

module bat_tranform () {
    translate ([-1, -BOTTOM_L+20, 0]) rotate ([0, 0, 90]) children ();
}

module breadb_transform () {
    translate ([25, -BOTTOM_L/2, 0]) children ();
}

module buttons_transform () {
    translate ([0, 16, 0]) {
        // Cross
        translate ([-30, 0, 0]) for (r=[0:90:360-1]) {
            rotate ([0, 0, r]) translate ([0, 2, 0]) rotate ([0, 0, 45]) children ();
        }
        // AB
        translate ([22-1, -2, 0]) rotate ([0, 0, -45]) children ();
        translate ([37+1, 2, 0]) rotate ([0, 0, 90+45]) children ();
    }
}

module roundrect (w, l, h, r) {
    hull () for (x=[-w/2+r, w/2-r]) for (y=[-l/2+r, l/2-r]) {
        translate ([x, y, 0]) cylinder (h, r=r);
    }
}

module screen_transform () {
    translate ([0, 16, 0]) children ();
}

module switch (h=SWITCH_H, offset=0) {
    translate ([-SWITCH_W/2-offset, TOP_L-SWITCH_L-1.5-offset, 0]) {
        cube ([SWITCH_W+offset*2, SWITCH_L+offset*2, h]);
    }
}

module speaker (h=SPEAKER_H, r=SPEAKER_R) {
    translate ([-MAIN_W/2+1, TOP_L/2, SPEAKER_R+0.75]) {
        rotate ([0, 90, 0]) cylinder (h, r=r);
    }
}

module t3_body () {
    union () {
        difference () {
            union () {
                // Base plate
                main_footprint (1);
                // Button Supports
                btn_pad_screws_transform () {
                    xpad_transform () cylinder (MAIN_H-4, r=SCREW_SUPPORT_R);
                    ab_transform () cylinder (MAIN_H-4, r=SCREW_SUPPORT_R);
                }
                // Screen Support
                screen_transform () {
                    h = MAIN_H-3;
                    difference () {
                        $fn = 20;
                        roundrect (33, 33, h, 5);
                        translate ([0, 0, 1]) roundrect (30, 30, 100, 4);
                        translate ([-20, 5, 4]) cube ([20, 10, 100]);
                    }
                    for (y=[-5, 5]) translate ([-16.5, y-0.5, 0]) {
                        cube ([33, 1, h-2]);
                    }
                }
                // Little Hooks
                for (x=[-30, 0, 30]) translate ([x, -BOTTOM_L, 0]) {
                    translate ([-2, 0, 1]) cube ([4, 2, 3]);
                    translate ([-2, 0, 3]) cube ([4, 3, 1]);
                    translate ([-2, 3, 3]) rotate ([45*5, 0, 0]) { 
                        translate ([0, 0, -1]) cube ([4, 3, 1]);
                    }
                }
                // Switch Support
                for (s=[-1, 1]) translate ([(SWITCH_H-1)*s-2, TOP_L-SWITCH_L-2.5, 0]) {
                    cube ([4, SWITCH_L+2, MAIN_H-3]);
                }
                // Speaker Support
                translate ([-MAIN_W/2+1, TOP_L/2-SPEAKER_R-2, 0]) union () {
                    cube ([SPEAKER_H+1.5, SPEAKER_R*2+4, SPEAKER_R-0.5]);
                    translate ([1, 0, 0]) {
                        cube ([SPEAKER_H-1.5, SPEAKER_R*2+4, SPEAKER_R*13/8]);
                    }
                }
            }
            // Breadboard Screw Holes
            breadb_transform () for (y=[-19, 19]) {
                translate ([0, y, -1]) cylinder (100, r=SCREW_LOOSE_R, $fn=10);
            }
            // Button Pad Screw Holes
            btn_pad_screws_transform () translate ([0, 0, 1]) {
                xpad_transform () cylinder (100, r=SCREW_TIGHT_R, $fn=10);
                ab_transform () cylinder (100, r=SCREW_TIGHT_R, $fn=10);
            }
            // Switch Hole
            translate ([0, 0, MAIN_H-SWITCH_H]) {
                switch (offset=0.5);
            }
            // Speaker Hole
            speaker (SPEAKER_H+0.5, r=SPEAKER_R+0.5);
        }

        // Perimeter Wall
        difference () {
            h = MAIN_H-3;
            main_footprint (h);
            translate ([0, 0, -1]) main_footprint (100, offset=1);
            // No Wall on the Bottom
            translate ([-100, -h, h+1]) rotate ([0, 90, 0]) cylinder (200, r=h);
            translate ([-50, -100-h, -1]) cube ([100, 100, 100]);
            // Speaker Hole
            translate ([-50, 0, 0]) speaker (100, r=2, $fn=10);
        }
    }
}

module btn_pad_screws_transform () {
    for (y=[-17, 17]) translate ([0, y, 0]) children ();
}

module xpad_transform () {
    translate ([-30, 15, 0]) children();
}

module ab_transform () {
    translate ([30, 15, 0]) children();
}

module btn_pad_base () {
    union () {
        intersection () {
            rotate ([0, 0, 45]) translate ([-25/2, -25/2]) cube ([25, 25, 2]);
            translate ([-26/2, -26/2]) cube ([26, 26, 2]);
        }
        hull () btn_pad_screws_transform () cylinder (1, r=5);
    }
}

module button_leg_holes () {
    for (x=[0, 6]) for (y=[0.5, 5.5]) {
        translate ([x, y, 0]) cylinder (100, r=1, $fn=10);
    }
}

module one_btn_pad () {
    translate ([-.5, -.5, 1]) cube ([6+1, 6+1, 3]);
    translate ([0, 0, -1]) button_leg_holes ();
}

module t3_xpad_pad () {
    difference () {
        xpad_transform () btn_pad_base ();
        buttons_transform () one_btn_pad ();
        xpad_transform () btn_pad_screws_transform () translate ([0, 0, -20]) {
            cylinder (100, r=SCREW_LOOSE_R, $fn=10);
        }
    }
}

module t3_ab_pad () {
    difference () {
        ab_transform () btn_pad_base ();
        buttons_transform () one_btn_pad ();
        ab_transform () btn_pad_screws_transform () translate ([0, 0, -20]) {
            cylinder (100, r=SCREW_LOOSE_R, $fn=10);
        }
    }
}

module t3_face () {
    scale ([-1, 1, 1]) intersection () {
        difference () {
            union () {
                // Main Face
                main_footprint (1);
                // Perimeter Wall
                difference () {
                    main_footprint (3);
                    main_footprint (100, 1);
                }
                // Button Walls
                buttons_transform () translate ([-2, -2, 0]) cube ([10, 10, 3]);
                // Screw Walls
                intersection () {
                    btn_pad_screws_transform () {
                        xpad_transform () cylinder (3, r=SCREW_SUPPORT_R, $fn=10);
                        ab_transform () cylinder (3, r=SCREW_SUPPORT_R, $fn=10);
                    }
                    translate ([-50, 3, 0]) cube ([100, 100, 100]);
                }
                // Alignment Pegs
                for (x=[-1, 1]) translate([(MAIN_W/2-3)*x-2, 0, 0]) {
                    cube ([4, 4, 5]);
                }
                // Screen Wall
                screen_transform () roundrect (34, 34, 3, 5);
                // Switch Wall
                switch (3, offset=1.5);
            }
            translate ([0, 0, -1]) {
                // Screw Holes
                btn_pad_screws_transform () {
                    xpad_transform () cylinder (100, r=SCREW_LOOSE_R, $fn=10);
                    ab_transform () cylinder (100, r=SCREW_LOOSE_R, $fn=10);
                }
                // Button Holes
                buttons_transform () {
                    cube ([6, 6, 100]);
                    translate ([0, 0, 2]) button_leg_holes ();
                }
                // Screen Hole
                screen_transform () for (x=[-1, 0, 1]) for (y=[-1, 0, 1]) {
                    translate ([x*9.5, y*9.5, -1]) roundrect (8.5, 8.5, 100, 1);
                }
                // Switch Hole
                switch (100, offset=0.4);
            }
        }
        translate ([-50, 0, 0]) cube ([100, 100, 100]);
    }
}

union () {
    t3_body ();
    translate ([60, 0, 0]) flexbatterAA(n=3);
    translate ([95, -50, 0]) t3_xpad_pad ();
    translate ([65, -50, 0]) t3_ab_pad ();
    translate ([0, -125, 0]) t3_face ();
}

% union () {
    translate ([0, 0, 2.1]) bat_tranform () flexbatterAA(n=3);
    breadb_transform () translate ([-31/2, -58/2, 10]) cube ([31, 58, 7]);
    translate ([0, 0, MAIN_H-3]) buttons_transform () cube ([6, 6, 3]);
    translate ([0, 0, MAIN_H-7]) switch ();
    translate ([0, 0, MAIN_H-4]) { t3_xpad_pad (); t3_ab_pad (); }
    translate ([0, 0, MAIN_H]) rotate ([0, 180, 0]) t3_face ();
    speaker ();
}
