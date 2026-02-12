"""
Test suite that compiles example GameBoy programs to verify they produce working .gb ROMs.

These examples represent the patterns from the system prompt. If these compile,
LLM-generated code following the same patterns should compile too.
"""

import pytest
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
WKDIR = PROJECT_ROOT / "wkdir"
OUT_DIR = PROJECT_ROOT / "out"
COMPILE_SCRIPT = PROJECT_ROOT / "compile.sh"
LCC = PROJECT_ROOT / "gbdk" / "bin" / "lcc"


def compile_c_code(c_code: str, test_name: str) -> bool:
    """Write C code to wkdir/file.c, compile it, return success status."""
    # Write source
    work_file = WKDIR / "file.c"
    work_file.write_text(c_code)

    # Clean previous output
    out_gb = OUT_DIR / "out.gb"
    if out_gb.exists():
        out_gb.unlink()

    # Compile
    result = subprocess.run(
        ["bash", str(COMPILE_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=30
    )

    success = out_gb.exists()

    if success:
        # Rename to test-specific name
        final = OUT_DIR / f"test_{test_name}.gb"
        if final.exists():
            final.unlink()
        out_gb.rename(final)
        print(f"  ✓ {test_name}: compiled ({final.stat().st_size:,} bytes)")
    else:
        err_file = WKDIR / "err.txt"
        errors = err_file.read_text() if err_file.exists() else "No error output"
        print(f"  ✗ {test_name}: FAILED")
        print(f"    {errors[:500]}")

    return success


@pytest.fixture(autouse=True)
def check_gbdk():
    """Skip all tests if GBDK is not installed."""
    if not LCC.exists():
        pytest.skip(f"GBDK not found at {LCC}")


class TestMinimalExamples:
    """Test the minimal examples from the system prompt."""

    def test_hello_world_text(self):
        """Minimal text example from system prompt."""
        code = '''
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>

void main(void) {
    color(BLACK, WHITE, SOLID);
    gotogxy(3, 4);
    gprintf("Hello GameBoy!");
    gotogxy(2, 8);
    gprintf("Press START");
    waitpad(J_START);
}
'''
        assert compile_c_code(code, "hello_world")

    def test_interactive_circle(self):
        """Graphics + game loop example from system prompt."""
        code = '''
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>

void main(void) {
    uint8_t x = 80, y = 72;
    uint8_t pad;

    color(BLACK, WHITE, SOLID);
    gotogxy(2, 0);
    gprintf("Use D-pad to move");

    while(1) {
        color(WHITE, WHITE, SOLID);
        circle(x, y, 5, M_FILL);

        pad = joypad();
        if (pad & J_UP    && y > 10)  y--;
        if (pad & J_DOWN  && y < 138) y++;
        if (pad & J_LEFT  && x > 6)   x--;
        if (pad & J_RIGHT && x < 154) x++;

        color(BLACK, WHITE, SOLID);
        circle(x, y, 5, M_FILL);

        vsync();
    }
}
'''
        assert compile_c_code(code, "interactive_circle")


class TestGamePatterns:
    """Test common game patterns that the LLM should generate."""

    def test_pong_game(self):
        """A simple Pong game - common request."""
        code = '''
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>
#include <string.h>

#define PADDLE_H 20
#define PADDLE_W 3
#define BALL_SIZE 3
#define SCREEN_W 160
#define SCREEN_H 144

uint8_t p1_y = 62;
uint8_t p2_y = 62;
uint8_t ball_x = 80, ball_y = 72;
int8_t ball_dx = 1, ball_dy = 1;
uint8_t score1 = 0, score2 = 0;

void draw_paddle(uint8_t x, uint8_t y, uint8_t clr) {
    color(clr, WHITE, SOLID);
    box(x, y, x + PADDLE_W, y + PADDLE_H, M_FILL);
}

void draw_ball(uint8_t clr) {
    color(clr, WHITE, SOLID);
    box(ball_x, ball_y, ball_x + BALL_SIZE, ball_y + BALL_SIZE, M_FILL);
}

void draw_scores(void) {
    color(BLACK, WHITE, SOLID);
    gotogxy(7, 0);
    gprintf("%u - %u", (uint8_t)score1, (uint8_t)score2);
}

void main(void) {
    uint8_t pad;

    color(BLACK, WHITE, SOLID);
    gotogxy(5, 8);
    gprintf("PONG");
    gotogxy(3, 10);
    gprintf("Press START");
    waitpad(J_START);
    waitpadup();

    // Clear and draw initial state
    color(WHITE, WHITE, SOLID);
    box(0, 0, 159, 143, M_FILL);
    draw_scores();
    color(DKGREY, WHITE, SOLID);
    line(80, 8, 80, 143);

    while(1) {
        // Erase
        draw_paddle(4, p1_y, WHITE);
        draw_paddle(153, p2_y, WHITE);
        draw_ball(WHITE);

        // Input
        pad = joypad();
        if (pad & J_UP   && p1_y > 9)   p1_y -= 2;
        if (pad & J_DOWN && p1_y < 123) p1_y += 2;

        // Simple AI
        if (ball_y > p2_y + 10 && p2_y < 123) p2_y++;
        if (ball_y < p2_y + 10 && p2_y > 9)   p2_y--;

        // Ball movement
        ball_x += ball_dx;
        ball_y += ball_dy;

        // Ball bounce top/bottom
        if (ball_y <= 9 || ball_y >= 140) ball_dy = -ball_dy;

        // Ball bounce paddles
        if (ball_x <= 8 && ball_y >= p1_y && ball_y <= p1_y + PADDLE_H) ball_dx = 1;
        if (ball_x >= 152 && ball_y >= p2_y && ball_y <= p2_y + PADDLE_H) ball_dx = -1;

        // Scoring
        if (ball_x <= 1) { score2++; ball_x = 80; ball_y = 72; ball_dx = 1; draw_scores(); }
        if (ball_x >= 158) { score1++; ball_x = 80; ball_y = 72; ball_dx = -1; draw_scores(); }

        // Draw
        draw_paddle(4, p1_y, BLACK);
        draw_paddle(153, p2_y, BLACK);
        draw_ball(BLACK);

        vsync();
    }
}
'''
        assert compile_c_code(code, "pong")

    def test_snake_game(self):
        """A snake game - another common request."""
        code = '''
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>
#include <stdlib.h>

#define GRID_SIZE 4
#define GRID_W (160 / GRID_SIZE)
#define GRID_H (128 / GRID_SIZE)
#define MAX_LEN 100
#define OFFSET_Y 16

uint8_t snake_x[100];
uint8_t snake_y[100];
uint8_t snake_len = 5;
int8_t dir_x = 1, dir_y = 0;
uint8_t food_x, food_y;
uint8_t score = 0;
uint8_t game_over = 0;

void place_food(void) {
    food_x = (rand() % (GRID_W - 2)) + 1;
    food_y = (rand() % (GRID_H - 2)) + 1;
}

void draw_cell(uint8_t gx, uint8_t gy, uint8_t clr) {
    uint8_t px = gx * GRID_SIZE;
    uint8_t py = gy * GRID_SIZE + OFFSET_Y;
    color(clr, WHITE, SOLID);
    box(px, py, px + GRID_SIZE - 1, py + GRID_SIZE - 1, M_FILL);
}

void main(void) {
    uint8_t i, pad, new_x, new_y;
    uint8_t delay_count;

    color(BLACK, WHITE, SOLID);
    gotogxy(5, 4);
    gprintf("SNAKE!");
    gotogxy(3, 8);
    gprintf("Press START");
    waitpad(J_START);
    waitpadup();

    // Init snake
    for (i = 0; i < snake_len; i++) {
        snake_x[i] = 10 - i;
        snake_y[i] = 10;
    }
    place_food();

    // Clear screen
    color(WHITE, WHITE, SOLID);
    box(0, 0, 159, 143, M_FILL);

    // Draw border
    color(DKGREY, WHITE, SOLID);
    box(0, OFFSET_Y, 159, 143, M_NOFILL);

    // Score header
    color(BLACK, WHITE, SOLID);
    gotogxy(0, 0);
    gprintf("Score: %u", (uint8_t)score);

    while (!game_over) {
        // Input
        pad = joypad();
        if (pad & J_UP    && dir_y != 1)  { dir_x = 0;  dir_y = -1; }
        if (pad & J_DOWN  && dir_y != -1) { dir_x = 0;  dir_y = 1;  }
        if (pad & J_LEFT  && dir_x != 1)  { dir_x = -1; dir_y = 0;  }
        if (pad & J_RIGHT && dir_x != -1) { dir_x = 1;  dir_y = 0;  }

        // New head position
        new_x = snake_x[0] + dir_x;
        new_y = snake_y[0] + dir_y;

        // Wall collision
        if (new_x == 0 || new_x >= GRID_W - 1 || new_y == 0 || new_y >= GRID_H - 1) {
            game_over = 1;
            break;
        }

        // Self collision
        for (i = 0; i < snake_len; i++) {
            if (snake_x[i] == new_x && snake_y[i] == new_y) {
                game_over = 1;
                break;
            }
        }
        if (game_over) break;

        // Erase tail
        if (new_x == food_x && new_y == food_y) {
            if (snake_len < MAX_LEN) snake_len++;
            score++;
            place_food();
            draw_cell(food_x, food_y, DKGREY);
            color(BLACK, WHITE, SOLID);
            gotogxy(7, 0);
            gprintf("%u  ", (uint8_t)score);
        } else {
            draw_cell(snake_x[snake_len - 1], snake_y[snake_len - 1], WHITE);
        }

        // Shift body
        for (i = snake_len - 1; i > 0; i--) {
            snake_x[i] = snake_x[i - 1];
            snake_y[i] = snake_y[i - 1];
        }
        snake_x[0] = new_x;
        snake_y[0] = new_y;

        // Draw head
        draw_cell(new_x, new_y, BLACK);

        // Draw food
        draw_cell(food_x, food_y, DKGREY);

        // Speed delay
        for (delay_count = 0; delay_count < 4; delay_count++) vsync();
    }

    // Game over screen
    color(BLACK, WHITE, SOLID);
    gotogxy(4, 9);
    gprintf("GAME OVER!");
    gotogxy(4, 11);
    gprintf("Score: %u", (uint8_t)score);
    waitpad(J_START);
}
'''
        assert compile_c_code(code, "snake")

    def test_wiki_page(self):
        """Text-heavy info page - tests gprintf layout."""
        code = '''
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>

uint8_t page = 0;

void draw_page(void) {
    color(WHITE, WHITE, SOLID);
    box(0, 0, 159, 143, M_FILL);

    color(BLACK, WHITE, SOLID);

    if (page == 0) {
        gotogxy(0, 0);
        gprintf("== CATS ==");
        gotogxy(0, 2);
        gprintf("The cat is a");
        gotogxy(0, 3);
        gprintf("small domestic");
        gotogxy(0, 4);
        gprintf("species of");
        gotogxy(0, 5);
        gprintf("carnivorous");
        gotogxy(0, 6);
        gprintf("mammal.");
        gotogxy(0, 8);
        gprintf("It is the only");
        gotogxy(0, 9);
        gprintf("domesticated");
        gotogxy(0, 10);
        gprintf("species in the");
        gotogxy(0, 11);
        gprintf("family Felidae.");
        gotogxy(0, 14);
        gprintf("Cats have been");
        gotogxy(0, 15);
        gprintf("kept since the");
        gotogxy(0, 16);
        gprintf("ancient times.");
        gotogxy(0, 17);
        gprintf("[A:next B:prev]");
    } else {
        gotogxy(0, 0);
        gprintf("== CATS p.2 ==");
        gotogxy(0, 2);
        gprintf("There are about");
        gotogxy(0, 3);
        gprintf("60 cat breeds");
        gotogxy(0, 4);
        gprintf("recognized by");
        gotogxy(0, 5);
        gprintf("registries.");
        gotogxy(0, 7);
        gprintf("Common breeds:");
        gotogxy(1, 9);
        gprintf("- Persian");
        gotogxy(1, 10);
        gprintf("- Siamese");
        gotogxy(1, 11);
        gprintf("- Maine Coon");
        gotogxy(1, 12);
        gprintf("- Bengal");
        gotogxy(1, 13);
        gprintf("- Ragdoll");
        gotogxy(0, 17);
        gprintf("[A:next B:prev]");
    }
}

void main(void) {
    uint8_t pad;

    draw_page();

    while(1) {
        pad = joypad();
        if (pad & J_A) {
            if (page < 1) { page++; draw_page(); }
            waitpadup();
        }
        if (pad & J_B) {
            if (page > 0) { page--; draw_page(); }
            waitpadup();
        }
        vsync();
    }
}
'''
        assert compile_c_code(code, "wiki_page")

    def test_drawing_visualization(self):
        """Visual art with shapes - tests drawing API."""
        code = '''
#include <gb/gb.h>
#include <gb/drawing.h>
#include <stdio.h>

void main(void) {
    uint8_t i;

    color(BLACK, WHITE, SOLID);
    gotogxy(2, 0);
    gprintf("Shape Gallery");

    // Concentric circles
    for (i = 5; i <= 30; i += 5) {
        color(BLACK, WHITE, SOLID);
        circle(40, 72, i, M_NOFILL);
    }

    // Filled boxes
    color(DKGREY, WHITE, SOLID);
    box(80, 40, 110, 60, M_FILL);
    color(BLACK, WHITE, SOLID);
    box(80, 40, 110, 60, M_NOFILL);

    color(LTGREY, WHITE, SOLID);
    box(95, 55, 125, 75, M_FILL);
    color(BLACK, WHITE, SOLID);
    box(95, 55, 125, 75, M_NOFILL);

    // Cross-hatching
    for (i = 85; i <= 150; i += 5) {
        color(DKGREY, WHITE, SOLID);
        line(i, 85, i - 15, 130);
    }

    // Border
    color(BLACK, WHITE, SOLID);
    box(80, 85, 155, 130, M_NOFILL);

    gotogxy(1, 17);
    gprintf("Press START exit");
    waitpad(J_START);
}
'''
        assert compile_c_code(code, "shapes")


if __name__ == "__main__":
    print("NightwingGameSim - Example Compilation Tests")
    print("=" * 60)

    if not LCC.exists():
        print(f"GBDK not found at {LCC}")
        exit(1)

    tests = [
        ("hello_world", TestMinimalExamples().test_hello_world_text),
        ("interactive_circle", TestMinimalExamples().test_interactive_circle),
        ("pong", TestGamePatterns().test_pong_game),
        ("snake", TestGamePatterns().test_snake_game),
        ("wiki_page", TestGamePatterns().test_wiki_page),
        ("shapes", TestGamePatterns().test_drawing_visualization),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError:
            failed += 1

    print()
    print(f"Results: {passed}/{passed + failed} passed")

