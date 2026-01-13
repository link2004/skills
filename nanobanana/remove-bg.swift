#!/usr/bin/env swift

import Foundation
import CoreImage
import Vision
import AppKit

/// Background Removal Tool (using macOS Vision Framework)
@available(macOS 14.0, *)
func removeBackground(inputPath: String, outputPath: String) -> Bool {
    // Load image
    guard let inputImage = NSImage(contentsOfFile: inputPath),
          let cgImage = inputImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("Error: Cannot load image: \(inputPath)")
        return false
    }

    let ciImage = CIImage(cgImage: cgImage)

    // Create mask generation request
    let request = VNGenerateForegroundInstanceMaskRequest()
    let handler = VNImageRequestHandler(ciImage: ciImage, options: [:])

    do {
        try handler.perform([request])

        guard let result = request.results?.first else {
            print("Error: Cannot generate mask")
            return false
        }

        // Generate mask
        let mask = try result.generateScaledMaskForImage(
            forInstances: result.allInstances,
            from: handler
        )

        let maskCIImage = CIImage(cvPixelBuffer: mask)

        // Erode mask by 1px to remove magenta edge residue
        guard let erodeFilter = CIFilter(name: "CIMorphologyMinimum") else {
            print("Error: Cannot create erosion filter")
            return false
        }
        erodeFilter.setValue(maskCIImage, forKey: kCIInputImageKey)
        erodeFilter.setValue(1.0, forKey: kCIInputRadiusKey)  // 1px erosion

        guard let erodedMask = erodeFilter.outputImage else {
            print("Error: Mask erosion failed")
            return false
        }

        // Apply mask to make background transparent
        let context = CIContext()

        // Create blend filter for mask application
        guard let blendFilter = CIFilter(name: "CIBlendWithMask") else {
            print("Error: Cannot create filter")
            return false
        }

        // Transparent background
        let transparentBackground = CIImage(color: CIColor(red: 0, green: 0, blue: 0, alpha: 0))
            .cropped(to: ciImage.extent)

        blendFilter.setValue(ciImage, forKey: kCIInputImageKey)
        blendFilter.setValue(transparentBackground, forKey: kCIInputBackgroundImageKey)
        blendFilter.setValue(erodedMask, forKey: kCIInputMaskImageKey)

        guard let outputCIImage = blendFilter.outputImage else {
            print("Error: Cannot generate output image")
            return false
        }

        // Save as PNG
        guard let cgOutput = context.createCGImage(outputCIImage, from: outputCIImage.extent) else {
            print("Error: Cannot create CGImage")
            return false
        }

        let bitmapRep = NSBitmapImageRep(cgImage: cgOutput)
        guard let pngData = bitmapRep.representation(using: .png, properties: [:]) else {
            print("Error: Cannot create PNG data")
            return false
        }

        try pngData.write(to: URL(fileURLWithPath: outputPath))
        print("Background removal complete: \(outputPath)")
        return true

    } catch {
        print("Error: \(error.localizedDescription)")
        return false
    }
}

// Main
func main() {
    let args = CommandLine.arguments

    if args.count < 3 {
        print("Usage: swift remove-bg.swift <input_image> <output_image>")
        print("Example: swift remove-bg.swift input.png output.png")
        exit(1)
    }

    let inputPath = args[1]
    let outputPath = args[2]

    if #available(macOS 14.0, *) {
        let success = removeBackground(inputPath: inputPath, outputPath: outputPath)
        exit(success ? 0 : 1)
    } else {
        print("Error: Requires macOS 14.0 or later")
        exit(1)
    }
}

main()
