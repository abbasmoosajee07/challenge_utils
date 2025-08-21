/* {header_text} */

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class {file_name} {{
    public static void main(String[] args) {{
        // Use the first argument if provided, otherwise default
        String fileName = (args.length >= 1) ? args[0] : "{text_placeholder}";
        File file = new File(fileName);

        System.out.println("Input Data:");
        try (Scanner sc = new Scanner(file)) {{
            while (sc.hasNextLine()) {{
                System.out.println(sc.nextLine());
            }}
        }} catch (FileNotFoundException e) {{
            System.err.println("File not found: " + fileName);
            e.printStackTrace();
        }}

        System.out.println("Hello, World!\\n- From Java");
    }}
}}
