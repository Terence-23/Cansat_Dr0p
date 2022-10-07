

fn complicated(height: f64) -> f64{
    // assume 0 wind speed and flat surface


}

fn simple(height: f64) ->(f64, f64) {

    // height: m/s
    // return (min, max) estimate assuming flat surface and lack of wind; not accurate

    const Min_speed: f64 = 8.3333;   // m/s
    const Max_speed: f64 = 19.4444; // m/s
    const Fall_speed: f64 = 6.0;   // m/s ; assumption

    let t = height / Fall_speed;
    (t * Min_speed, t * Max_speed)
}


fn main() {
    // callculation height is cmdline argument

    let cmd_line: Vec<String> = std::env::args().collect();
    let h: f64;

    let mut has_read_first_arg = false;
    h = cmd_line[1].parse::<f64>().unwrap();
    
    println!("height: {:#?}m", h);

    println!("simple: {:#?}[m]", simple(h))

}