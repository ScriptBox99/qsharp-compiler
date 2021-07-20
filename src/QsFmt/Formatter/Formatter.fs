﻿// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

module Microsoft.Quantum.QsFmt.Formatter.Formatter

open Antlr4.Runtime
open Microsoft.Quantum.QsFmt.Formatter.Errors
open Microsoft.Quantum.QsFmt.Formatter.ParseTree.Namespace
open Microsoft.Quantum.QsFmt.Formatter.Printer
open Microsoft.Quantum.QsFmt.Formatter.Rules
open Microsoft.Quantum.QsFmt.Formatter.Utils
open Microsoft.Quantum.QsFmt.Parser
open System.Collections.Immutable

/// <summary>
/// Parses the Q# source code into a <see cref="QsFmt.Formatter.SyntaxTree.Document"/>.
/// </summary>
let parse (source: string) =
    let tokenStream = source |> AntlrInputStream |> QSharpLexer |> CommonTokenStream

    let parser = QSharpParser tokenStream
    parser.RemoveErrorListener ConsoleErrorListener.Instance
    let errorListener = ListErrorListener()
    parser.AddErrorListener errorListener

    let documentContext = parser.document ()

    if List.isEmpty errorListener.SyntaxErrors then
        let tokens = tokenStream.GetTokens() |> ImmutableArray.CreateRange
        documentContext |> toDocument tokens |> Ok
    else
        errorListener.SyntaxErrors |> Error

[<CompiledName "Format">]
let format source =
    let formatDocument document =
        // Test whether there is data loss during parsing and unparsing
        if printer.Document document = source then
            // The actuall format process
            document
            |> curry collapsedSpaces.Document ()
            |> curry operatorSpacing.Document ()
            |> curry newLines.Document ()
            |> curry indentation.Document 0
            |> printer.Document
        // Report error if the unparsing result does match the original source
        else
            failwith (
                "The formater does not work properly. "
                + "Please let us know by filing a new issue in https://github.com/microsoft/qsharp-compiler/issues/new/choose."
            )

    parse source |> Result.map formatDocument

[<CompiledName "Identity">]
let identity source =
    parse source |> Result.map printer.Document
